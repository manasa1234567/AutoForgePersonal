# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* frontend/tsconfig.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build and runtime backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for building and psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Copy backend poetry files
COPY backend/pyproject.toml backend/poetry.lock* ./backend/

# Install Poetry
RUN pip install poetry

# Install dependencies (lock recreated if missing)
RUN cd backend && poetry config virtualenvs.create false && rm -f poetry.lock && poetry lock --no-interaction && poetry install --no-interaction --no-ansi --no-root

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend static files into backend static dir
COPY --from=frontend-build /app/frontend/build ./backend/app/static

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
