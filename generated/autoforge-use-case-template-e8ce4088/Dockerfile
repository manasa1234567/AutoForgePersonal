# Build stage
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/tsconfig.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Runtime stage
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/pyproject.toml backend/poetry.lock* ./backend/
RUN pip install poetry &&      cd backend &&      poetry config virtualenvs.create false &&      rm -f poetry.lock && poetry lock --no-interaction && poetry install --no-interaction --no-ansi --no-root

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend static files
COPY --from=frontend-build /app/frontend/build ./backend/app/static

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
