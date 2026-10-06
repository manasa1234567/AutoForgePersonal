"""Conservative local import checks; never execute generated application code."""
import ast
import posixpath


def _exports(tree: ast.Module) -> set[str] | None:
    names: set[str] = set()
    pending = list(tree.body)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == "__getattr__":
                return None  # PEP 562 dynamic exports
            names.add(node.name)
        elif isinstance(node, ast.Import):
            names.update(alias.asname or alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if any(alias.name == '*' for alias in node.names):
                return None
            names.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            # globals()/locals() mutation is intentionally opaque.
            if any(isinstance(part, ast.Call) for target in targets for part in ast.walk(target)):
                return None
            names.update(part.id for target in targets for part in ast.walk(target)
                         if isinstance(part, ast.Name) and isinstance(part.ctx, ast.Store))
        elif isinstance(node, ast.Expr) and not isinstance(node.value, ast.Constant):
            return None  # module initialization could install exports dynamically
        elif isinstance(node, (ast.If, ast.Try)):
            pending.extend(node.body)
            pending.extend(node.orelse)
            if isinstance(node, ast.Try):
                pending.extend(node.finalbody)
                for handler in node.handlers:
                    pending.extend(handler.body)
        elif not isinstance(node, (ast.Pass, ast.Expr)):
            return None  # unsupported module-level constructs: leave to runtime
    return names


def local_import_issues(files: dict[str, str]) -> list[str]:
    trees = {}
    for path, content in files.items():
        if path.endswith('.py'):
            try:
                trees[path] = ast.parse(content, filename=path)
            except SyntaxError:
                pass  # reported by the syntax check
    exports = {path: _exports(tree) for path, tree in trees.items()}
    issues = []
    for path, tree in trees.items():
        # Check unconditional imports only. Optional imports in try/except,
        # TYPE_CHECKING blocks and function-local imports need runtime context.
        for node in tree.body:
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            module_path = node.module.replace('.', '/')
            if node.level:
                parent = posixpath.dirname(path)
                for _ in range(node.level - 1):
                    parent = posixpath.dirname(parent)
                stem = posixpath.join(parent, module_path)
                candidates = [p for p in (stem + '.py', stem + '/__init__.py') if p in trees]
            else:
                # Accept only one matching source module; ambiguous monorepos
                # and external imports must be resolved by the actual runtime.
                suffixes = (module_path + '.py', module_path + '/__init__.py')
                candidates = [p for p in trees if any(p == s or p.endswith('/' + s) for s in suffixes)]
            if len(candidates) != 1:
                continue
            target = candidates[0]
            names = exports[target]
            if names is None:
                continue
            for alias in node.names:
                if alias.name == '*' or alias.name in names:
                    continue
                if target.endswith('/__init__.py'):
                    child = target[:-len('__init__.py')] + alias.name
                    if child + '.py' in files or any(p.startswith(child + '/') for p in files):
                        continue  # from package import submodule
                issues.append(
                    f"{path}:{node.lineno} imports {alias.name!r} from {node.module!r}, "
                    f"but {target} does not define or import that name. "
                    "Make the caller and implementation consistent; implement required behavior "
                    "rather than adding a placeholder or dropping approved features."
                )
    return issues
