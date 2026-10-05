# Multi-stage build for fullstack app (frontend and backend)

# Build frontend
FROM node:18-alpine3.17 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/. .
RUN npm run build

# Build backend
FROM python:3.11-slim AS backend-build
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app

# Final image
FROM python:3.11-slim
WORKDIR /app

# Copy backend
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /app/app ./app

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Install a simple HTTP server for frontend static files
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Setup nginx config for frontend static files
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 8080

# Start backend and nginx
# Use a simple script to start both
COPY backend/start.sh ./start.sh
RUN chmod +x ./start.sh

CMD ["./start.sh"]
