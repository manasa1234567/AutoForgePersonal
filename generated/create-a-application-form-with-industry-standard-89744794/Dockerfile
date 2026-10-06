# Stage 1: Build React frontend
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build backend image
FROM python:3.11-slim
# Set workdir
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/app ./app

# Copy frontend build output to backend static directory
COPY --from=frontend-build /app/frontend/build ./app/static

# Expose
EXPOSE 8080

# Start backend with uvicorn, static files served by FastAPI in /app/static
# Backend will listen on port 8080 and bind on all interfaces
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
