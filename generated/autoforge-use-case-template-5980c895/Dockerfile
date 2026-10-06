# Use official Python 3.11 image as base
FROM python:3.11-slim

# Install system dependencies including nodejs and npm for frontend build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and frontend package manifests
COPY ./backend/requirements.txt ./backend/requirements.txt
COPY ./frontend/package.json ./frontend/package.json
COPY ./frontend/package-lock.json ./frontend/package-lock.json

# Install backend dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Install frontend dependencies and build frontend
WORKDIR /app/frontend
RUN if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; else npm install; fi
RUN npm run build

# Copy backend source
WORKDIR /app/backend
COPY ./backend ./

# Move frontend build output to backend static folder
RUN mkdir -p ./static
RUN cp -r ../frontend/build/* ./static/

# Expose port 8080
EXPOSE 8080

# Run the backend app with uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
