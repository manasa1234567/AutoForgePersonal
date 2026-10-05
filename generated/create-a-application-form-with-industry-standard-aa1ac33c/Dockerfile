# Build and package full stack application

# Backend build stage
FROM python:3.11-slim as backend-build
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app

# Frontend build stage
FROM node:18-alpine as frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Final stage
FROM python:3.11-slim
WORKDIR /app

# Setup backend python packages
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Copy backend app directory
COPY --from=backend-build /app/app /app/app

# Setup frontend static files
COPY --from=frontend-build /frontend/dist /app/static

# Install runtime python packages usually needed
RUN pip install --no-cache-dir fastapi==0.115.12 uvicorn[standard]==0.34.2 pydantic==2.11.3 aiofiles starlette

# Combined ASGI app serves frontend static and backend api
RUN echo "from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.main import app as api_app

app = FastAPI()

app.mount('/static', StaticFiles(directory='./static'), name='static')
app.mount('/api', api_app)

@app.get('/')
async def root():
    return {'message': 'Application Form Fullstack Backend Running'}
" > main_combined.py

EXPOSE 8080
CMD ["uvicorn", "main_combined:app", "--host", "0.0.0.0", "--port", "8080"]
