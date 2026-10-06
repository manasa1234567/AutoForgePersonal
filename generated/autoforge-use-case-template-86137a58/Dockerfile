# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build backend
FROM python:3.11-slim AS backend-build
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

# Stage 3: Final runtime image
FROM python:3.11-slim
WORKDIR /app

# Copy backend dependencies
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build output
COPY --from=frontend-build /app/frontend/build /app/frontend/build

# Expose port
EXPOSE 8080

# Command to run backend server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
