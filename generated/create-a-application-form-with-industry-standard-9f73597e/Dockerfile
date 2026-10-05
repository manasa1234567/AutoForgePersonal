# Build stage for backend
FROM python:3.11-slim as backend-build
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend

# Build stage for frontend
FROM node:18-alpine as frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend ./frontend
RUN npm run build

# Final stage
FROM python:3.11-slim
WORKDIR /app

# Copy backend code and installed packages
COPY --from=backend-build /app/backend ./backend
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy frontend build output
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose port 8080
EXPOSE 8080

# Create ASGI entry file to serve both API and static frontend
RUN echo "from fastapi import FastAPI" > ./main.py && \
    echo "from fastapi.staticfiles import StaticFiles" >> ./main.py && \
    echo "from backend.main import app as api_app" >> ./main.py && \
    echo "app = FastAPI()" >> ./main.py && \
    echo "app.mount('/api', api_app)" >> ./main.py && \
    echo "app.mount('/', StaticFiles(directory='frontend/dist', html=True), name='frontend')" >> ./main.py

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
