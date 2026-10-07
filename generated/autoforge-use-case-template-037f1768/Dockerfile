# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; else npm install; fi
COPY frontend/ .
RUN npm run build

# Stage 2: Build backend
FROM python:3.11-slim AS backend-build
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/app

# Stage 3: Final image
FROM python:3.11-slim
WORKDIR /app

# Copy backend source and dependencies from build stage
COPY --from=backend-build /app/backend/app ./app
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy frontend build output
COPY --from=frontend-build /frontend/build ./frontend/build

# Install uvicorn
RUN pip install --no-cache-dir uvicorn[standard]==0.34.2

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
