"""Source-triggered optional dependency checks across Python manifest formats."""
import ast
import re
import tomllib


def uses_pydantic_email(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False  # The separate syntax check owns malformed source.
    modules = set()
    star_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split('.')[0] == 'pydantic':
            if any(item.name in {'EmailStr', 'NameEmail'} for item in node.names):
                return True
            star_import = star_import or any(item.name == '*' for item in node.names)
        if isinstance(node, ast.Import):
            modules.update(item.asname or item.name.split('.')[0] for item in node.names if item.name.split('.')[0] == 'pydantic')
    for node in ast.walk(tree):
        if star_import and isinstance(node, ast.Name) and node.id in {'EmailStr', 'NameEmail'}:
            return True
        if isinstance(node, ast.Attribute) and node.attr in {'EmailStr', 'NameEmail'}:
            value = node.value
            while isinstance(value, ast.Attribute):
                value = value.value
            if isinstance(value, ast.Name) and value.id in modules:
                return True
    return False


def _requirements(lines):
    result = {}
    for line in lines:
        match = re.match(r'^\s*([\w.-]+)(?:\[([^]]+)\])?\s*(.*)$', line)
        if match:
            name = re.sub(r'[-_.]+', '-', match[1]).lower()
            version = match[3].split(';', 1)[0].strip()
            old_version, old_extras = result.get(name, ('', set()))
            result[name] = (','.join(v for v in (old_version, version) if v),
                            old_extras | {item.strip().lower() for item in (match[2] or '').split(',') if item.strip()})
    return result


def optional_dependency_issues(artifacts: dict[str, str]) -> list[str]:
    issues = []
    for path, content in artifacts.items():
        name = path.rsplit('/', 1)[-1]
        root = path.rsplit('/', 1)[0] + '/' if '/' in path else ''
        if name == 'pyproject.toml':
            try:
                project = tomllib.loads(content)
            except tomllib.TOMLDecodeError:
                continue
            metadata, tool = project.get('project', {}), project.get('tool', {})
            poetry = tool.get('poetry', {}) if isinstance(tool, dict) else {}
            pep = metadata.get('dependencies', []) if isinstance(metadata, dict) else []
            declared = poetry.get('dependencies', {}) if isinstance(poetry, dict) else {}
            if not isinstance(pep, list) or not all(isinstance(item, str) for item in pep) or not isinstance(declared, dict):
                issues.append(f'{path}: invalid Python dependency declarations; use valid project dependency lists or Poetry tables.')
                continue
            dependencies = _requirements(pep)
            for distribution, value in declared.items():
                if isinstance(value, str):
                    dependencies[re.sub(r'[-_.]+', '-', distribution).lower()] = (value, set())
                elif isinstance(value, dict):
                    extras = value.get('extras', [])
                    if not isinstance(extras, list) or not all(isinstance(extra, str) for extra in extras):
                        issues.append(f'{path}: invalid extras for {distribution}; declare an array of extra names.')
                        continue
                    dependencies[re.sub(r'[-_.]+', '-', distribution).lower()] = (str(value.get('version', '')), {extra.lower() for extra in extras})
        elif name.endswith(('.txt', '.in')) and (name.startswith('requirements')
                or root.rstrip('/').rsplit('/', 1)[-1] in {'requirements', 'requirements.d'}):
            dependencies = _requirements(content.splitlines())
            if root.rstrip('/').rsplit('/', 1)[-1] in {'requirements', 'requirements.d'}:
                root = root.rstrip('/').rsplit('/', 1)[0] + '/' if '/' in root.rstrip('/') else ''
        else:
            continue
        used = any(p.startswith(root) and p.endswith('.py')
                   and not any(part in {'test', 'tests', '__tests__'} for part in p.split('/'))
                   and not p.rsplit('/', 1)[-1].startswith('test_')
                   and uses_pydantic_email(source) for p, source in artifacts.items())
        if not used:
            continue
        pydantic, extras = dependencies.get('pydantic', ('', set()))
        email, _ = dependencies.get('email-validator', ('', set()))
        fastapi_extras = dependencies.get('fastapi', ('', set()))[1]
        v2 = bool(re.match(r'^\s*(?:\^|~=?|==|>=|>)?\s*2(?:\.|\s|,|$)', pydantic))
        if 'email-validator' not in dependencies and 'email' not in extras and not fastapi_extras.intersection({'standard', 'all'}):
            issues.append(f'{path}: Pydantic EmailStr/NameEmail requires a runtime email-validator dependency or pydantic[email]. '
                          + ('Pydantic 2 requires email-validator>=2.0; declare a compatible dependency.' if v2 else 'Declare its owning distribution, not an imported module.'))
        elif v2 and (re.match(r'^\s*(?:\^|~=?|==)?\s*1(?:\.|$)', email)
                     or re.search(r'(?:^|,)\s*<\s*2(?:\.0(?:\.0)?\s*(?:,|$)|\s*(?:,|$))', email)
                     or re.search(r'(?:^|,)\s*<=\s*1(?:\.|\s|,|$)', email)):
            issues.append(f'{path}: Pydantic 2 EmailStr/NameEmail requires email-validator>=2.0, but email-validator is {email!r}. '
                          'Correct the dependency constraint in the owning manifest and regenerate its lock; final-image library copies can overwrite a newer runtime install.')
    return issues
