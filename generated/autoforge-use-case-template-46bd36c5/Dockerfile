# Stage 1: Build stage for frontend
FROM node:18-alpine as build-frontend

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy backend dependency files
COPY backend/pyproject.toml backend/poetry.lock ./

# Install Python dependencies with poetry, no dev
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy backend source
COPY backend/app ./app

# Copy frontend build output
COPY --from=build-frontend /app/frontend/build /app/backend/app/static

# Expose port 8080
EXPOSE 8080

# Entrypoint
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
