# Build stage
FROM node:20.6-alpine as frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend build stage
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source
COPY backend ./backend

# Copy frontend build from frontend-build stage
COPY --from=frontend-build /app/dist /app/backend/static

# Expose port
EXPOSE 8080

# Start uvicorn
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
