"""Stage lock resolution in Docker; never edit the reviewed project/manifests."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.agents.poetry_packaging import resolve_poetry_before_install

if __name__ == "__main__":
    source, target = map(Path, sys.argv[1:3])
    target.write_text(resolve_poetry_before_install(source.read_text(encoding="utf-8")), encoding="utf-8")
