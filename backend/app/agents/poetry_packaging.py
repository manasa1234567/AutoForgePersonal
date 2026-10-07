"""Resolve generated Poetry locks using the selected image's actual toolchain."""
import json
import re
import shlex


def _unquoted(text: str, offset: int) -> bool:
    quote = None
    escaped = False
    for char in text[:offset]:
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
    return quote is None


def resolve_poetry_before_install(dockerfile: str) -> str:
    """Keep manifests/install flags intact; replace untrusted locks in-image.

    RUN arguments inside strings/heredocs and conditional shell programs are
    not interpreted. This applies to generated projects, whose model-authored
    lockfiles are hints rather than verified package-manager output.
    """
    logical = re.sub(r"\\\r?\n", " ", dockerfile)
    output = []
    for line in logical.splitlines():
        match = re.match(r"^(\s*RUN\s+)(.*)$", line, re.I)
        if not match:
            output.append(line)
            continue
        prefix, command = match.groups()
        if "<<" in command or "`" in command or "$(" in command or re.match(r"(?:if|for|while|case)\b", command):
            output.append(line)
            continue
        if command.startswith("["):
            try:
                args = json.loads(command)
            except ValueError:
                args = []
            if isinstance(args, list) and all(isinstance(arg, str) for arg in args):
                if args[:2] == ["poetry", "install"]:
                    line = prefix + json.dumps(["sh", "-c", "rm -f poetry.lock && poetry lock --no-interaction && " + shlex.join(args)])
                elif len(args) == 3 and args[0] in {"sh", "/bin/sh", "bash", "/bin/bash"} and args[1] == "-c":
                    nested = resolve_poetry_before_install("RUN " + args[2]).strip()[4:]
                    line = prefix + json.dumps([args[0], "-c", nested])
            output.append(line)
            continue
        pattern = re.compile(r"(^|&&\s*|;\s*)((?:python(?:3)?\s+-m\s+)?poetry)\s+install\b")
        def replace(found):
            if not _unquoted(command, found.start()):
                return found[0]
            # Idempotence for the exact platform-inserted chain.
            if command[:found.start()].rstrip().endswith("poetry lock --no-interaction"):
                return found[0]
            return found[1] + "rm -f poetry.lock && " + found[2] + " lock --no-interaction && " + found[2] + " install"
        output.append(prefix + pattern.sub(replace, command))
    return "\n".join(output) + ("\n" if dockerfile.endswith("\n") else "")
