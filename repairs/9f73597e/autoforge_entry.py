from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.main import app as api_app

site = Path(__file__).parent / "frontend" / "dist"
app = FastAPI()
app.mount("/assets", StaticFiles(directory=site / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(site / "index.html")


# Keep /submit at its existing path so the generated form can reach it.
app.mount("/", api_app)
