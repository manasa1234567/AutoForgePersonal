from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="Hello World App")

# Mount the frontend build folder as static
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    @app.get("/", response_class=HTMLResponse)
    async def no_frontend():
        return "<html><body><h1>Hello World</h1><p>Static frontend not built or missing.</p></body></html>"

@app.get("/health")
async def health():
    return {"status": "ok"}
