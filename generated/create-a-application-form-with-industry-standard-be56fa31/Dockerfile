# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* frontend/yarn.lock* ./
# Use npm or yarn depending on lock file presence
RUN if [ -f package-lock.json ]; then npm ci; elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; else npm install; fi
COPY frontend/ .
RUN npm run build

# Stage 2: Build backend
FROM python:3.11-slim AS backend-build
WORKDIR /backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app

# Stage 3: Final image
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy backend dependencies and app
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /backend/app ./app

# Copy frontend build output
COPY --from=frontend-build /frontend/dist ./frontend/dist

# Expose port 8080
EXPOSE 8080

# Start uvicorn server which serves backend and frontend (frontend static files to be served separately or by frontend server)
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --proxy-headers
