"""Frontend scope comes from the approved blueprint, not generated file presence."""
import re


def expects_browser_ui(frontend: str) -> bool:
    value = re.sub(r"^recommended:\s*", "", frontend.strip().lower())
    if re.match(r"^(?:none|no frontend|not applicable|n/a|api[- ]only|backend[- ]only)(?:$|[\s(:])", value):
        return False
    return bool(re.search(r"\b(?:react|angular|vue|svelte|next\.?js|nuxt|html|blazor|razor|web|browser|frontend)\b", value))


def frontend_issues(files: dict[str, str], frontend: str) -> list[str]:
    if not expects_browser_ui(frontend):
        return []
    for path in files:
        parts = path.lower().split('/')
        if any(part in {'tests', '__tests__', 'node_modules', '.git'} for part in parts):
            continue
        if re.search(r"\.(?:test|spec)\.", parts[-1]):
            continue
        if path.lower().endswith(('.html', '.htm', '.jsx', '.tsx', '.vue', '.svelte', '.razor', '.cshtml', '.erb')):
            return []
        if path.lower().endswith('.js') and any(part in {'frontend', 'client', 'web', 'src', 'pages'} for part in parts[:-1]):
            return []
    return [
        f"Approved frontend is {frontend!r}, but generated artifacts contain no browser UI source. "
        "Generate the complete approved frontend and its dependencies, package it with the backend, "
        "and serve the UI at /. A JSON status response, API docs or placeholder page does not satisfy the approved UI. "
        "Preserve existing backend features and API routes."
    ]
