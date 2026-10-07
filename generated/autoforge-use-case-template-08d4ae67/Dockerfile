# Build stage for frontend
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/tsconfig.json ./
RUN npm install typescript@^4.9.5 @types/react@^18.0.27 @types/react-dom@^18.0.10 react@^18.2.0 react-dom@^18.2.0 react-scripts@5.0.1
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm run build

# Build stage for backend
FROM python:3.11-slim as backend-build
WORKDIR /app
COPY app ./app
COPY pyproject.toml ./
RUN python -m pip install --upgrade pip poetry && poetry config virtualenvs.create false && rm -f poetry.lock && poetry lock --no-interaction && poetry install --no-root --no-interaction --no-ansi

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
# Install runtime dependencies
RUN python -m pip install --no-cache-dir fastapi uvicorn[standard] psycopg[binary]

# Copy backend code and dependencies
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /app/app /app/app

# Copy frontend build output
COPY --from=frontend-build /app/frontend/build /app/frontend/build

EXPOSE 8080
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
