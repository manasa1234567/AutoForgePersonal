# Multi-stage build

# Build frontend
FROM node:20-alpine as frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm run build

# Build backend
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy frontend build output to serve statically
COPY --from=frontend-build /app/frontend/build/ ./backend/static/

# Use Uvicorn to run backend and serve frontend static files
# The FastAPI backend will serve the static frontend
ENV HOST 0.0.0.0
ENV PORT 8080

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
