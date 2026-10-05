# Build stage
FROM node:18-alpine as build-frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.11-slim

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend code
COPY backend /app/backend

# Copy frontend build output
COPY --from=build-frontend /app/build /app/frontend/build

WORKDIR /app/backend

# Expose API port
EXPOSE 8080

# Start backend with uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

EXPOSE 8080
