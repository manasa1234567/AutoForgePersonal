# Use official python base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy backend requirements and install them
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source
COPY backend/app ./backend/app

# Copy frontend source
COPY frontend ./frontend

# Install frontend dependencies and build frontend
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    cd frontend && npm install && npm run build

# Use a lightweight official python image to run backend
FROM python:3.11-slim as runner

WORKDIR /app

COPY --from=0 /app/backend ./backend
COPY --from=0 /app/frontend/dist ./frontend/dist

RUN pip install --no-cache-dir fastapi uvicorn starlette

# To serve frontend statically via python uvicorn backend. We'll mount static at /

# Startup script to run backend with Uvicorn and serve frontend static
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]

EXPOSE 8080
