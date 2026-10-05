"""Narrow source diagnostics; these do not replace the TypeScript compiler."""

import re

from ..models.schemas import CriticFinding


def form_error_findings(artifacts: dict[str, str]) -> list[CriticFinding]:
    """Detect literal error messages assigned to boolean/number form fields.

    Restrict this check to simple local interfaces and explicitly typed error
    maps. Leave imported types, unions, nested types and general expressions to
    the compiler rather than guessing their meaning.
    """
    findings = []
    for path, content in artifacts.items():
        if not path.endswith((".ts", ".tsx")):
            continue
        # Comments are not executable assignments.
        source = re.sub(r"/\*[\s\S]*?\*/|(?m:^\s*//[^\n]*)", "", content)
        interfaces = {}
        for match in re.finditer(r"\binterface\s+(\w+)\s*\{([^{}]*)\}", source):
            fields = re.findall(r"\b(\w+)\??\s*:\s*(boolean|number)\s*[;\n]", match[2])
            interfaces[match[1]] = dict(fields)
        for declaration in re.finditer(
            r"(?m)^\s*(?:const|let)\s+(\w*[Ee]rrors)\s*:\s*Partial\s*<\s*(\w+)\s*>\s*=\s*\{\s*\}",
            source,
        ):
            variable, type_name = declaration.groups()
            for field, field_type in interfaces.get(type_name, {}).items():
                assignment = re.search(
                    rf"(?:^|[;){{}}])\s*{re.escape(variable)}\.{re.escape(field)}\s*=\s*(['\"])[^\n]*?\1\s*;",
                    source[declaration.end():], re.MULTILINE,
                )
                if assignment:
                    findings.append(CriticFinding(
                        severity="High", file=path,
                        issue=(f"{variable}.{field} receives a string error message, but "
                               f"Partial<{type_name}> gives this field type {field_type}. "
                               "This causes a TypeScript assignment error (TS2322)."),
                        recommendation=(
                            f"Use Partial<Record<keyof {type_name}, string>> for the error map "
                            "and its matching React error state. Keep the actual form data types "
                            "unchanged. Do not disable type checking or use any to hide the error."
                        ),
                    ))
    return findings
