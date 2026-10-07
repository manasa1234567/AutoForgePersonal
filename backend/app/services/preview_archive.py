"""Stream source files and a standalone preview without gateway idle timeouts."""
import asyncio
from io import UnsupportedOperation
import re
import zipfile

from .ui_preview import wrap_preview


class _ZipBuffer:
    def __init__(self):
        self.buffer = bytearray()
        self.position = 0

    def write(self, data):
        self.buffer.extend(data)
        self.position += len(data)
        return len(data)

    def tell(self):
        return self.position

    def seek(self, *args):
        raise UnsupportedOperation('Streaming ZIP')

    def flush(self):
        pass

    def drain(self):
        data = bytes(self.buffer)
        self.buffer.clear()
        return data


def safe_artifacts(files):
    result = {}
    for path, content in files.items():
        normalized = path.replace('\\', '/')
        if (normalized.startswith('/') or re.match(r'^[A-Za-z]:', normalized)
                or any(part in {'', '.', '..'} for part in normalized.split('/'))):
            continue
        result[normalized] = content
    return result


def _available_name(files, preferred):
    names = {name.casefold() for name in files}
    if preferred.casefold() not in names:
        return preferred
    stem, extension = preferred.rsplit('.', 1)
    number = 1
    while f'{stem}-{number}.{extension}'.casefold() in names:
        number += 1
    return f'{stem}-{number}.{extension}'


async def preview_zip(build, artifacts, previews, heartbeat=5):
    artifacts = safe_artifacts(artifacts)
    preview_name = _available_name(artifacts, 'preview.html')
    readme_name = _available_name(artifacts, 'PREVIEW_README.md')
    buffer = _ZipBuffer()
    pending = None
    try:
        with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zipped:
            for path, content in artifacts.items():
                zipped.writestr(path, content)
                yield buffer.drain()
            pending = asyncio.create_task(previews.html(build, artifacts))
            info = zipfile.ZipInfo(preview_name)
            # Stored bytes allow legal whitespace heartbeats while the model
            # prepares HTML. Compression buffering would hide those bytes.
            info.compress_type = zipfile.ZIP_STORED
            with zipped.open(info, 'w') as member:
                yield buffer.drain()
                while not pending.done():
                    finished, _ = await asyncio.wait({pending}, timeout=heartbeat)
                    if not finished:
                        member.write(b'\n')
                        yield buffer.drain()
                try:
                    body = await pending
                except Exception:
                    body = wrap_preview(build.title, '<!doctype html><html><body><h1>Preview unavailable</h1><p>The original project files are included. Open Preview UI on the build page and retry preview generation.</p></body></html>')
                member.write(body.encode('utf-8'))
            yield buffer.drain()
            zipped.writestr(readme_name, f'''# Offline UI preview

Extract the entire ZIP and double-click `{preview_name}` in your browser.
No Node, Python, backend server or installation is required for the preview.

This is an interactive visual interpretation of the generated frontend.
Backend-driven operations, authentication and database changes use fictional
sample data held in memory. Changes reset when the page reloads. This is not
evidence that the application compiled, passed tests or deployed successfully.

Original application and test files remain included for running the real app.
If the preview is unavailable, use Preview UI on the build page to regenerate
it, then download the ZIP again. Source downloads remain available even if
preview generation fails.
''')
            yield buffer.drain()
        yield buffer.drain()
    finally:
        if pending and not pending.done():
            pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)
