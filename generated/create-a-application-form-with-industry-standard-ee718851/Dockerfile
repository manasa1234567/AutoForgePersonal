# Build frontend
FROM node:18 as frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Build backend
FROM python:3.11-slim as backend-build
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Final image
FROM python:3.11-slim
WORKDIR /app

# Copy backend
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /app /app

# Copy frontend build into /app/frontend-static
COPY --from=frontend-build /app/build /app/frontend-static

ENV FRONTEND_STATIC_DIR=/app/frontend-static

# Install a simple static server (uvicorn will serve backend; serve frontend with middleware)
RUN pip install fastapi uvicorn

# Custom app entrypoint
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]

EXPOSE 8080
