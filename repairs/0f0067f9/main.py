from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello")
def hello_world():
    return {"message": "Hello World"}


# Dockerfile copies the built UI here. Register after API routes so /hello
# keeps returning JSON while / and /assets/... serve the actual frontend.
app.mount("/", StaticFiles(directory="/app/frontend/dist", html=True), name="frontend")
