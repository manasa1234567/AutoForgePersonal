# Use a multi-stage build: frontend and backend combined in one container

### Build Frontend ###
FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

### Build Backend ###
FROM python:3.11-slim AS backend-build
WORKDIR /backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app

### Final image ###
FROM python:3.11-slim

WORKDIR /app

# Copy backend app
COPY --from=backend-build /backend/app ./app
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=frontend-build /frontend/dist ./frontend_dist

# Install a lightweight static server for the frontend
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
RUN rm /etc/nginx/sites-enabled/default
COPY backend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["/bin/sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;' --no-daemon"]
