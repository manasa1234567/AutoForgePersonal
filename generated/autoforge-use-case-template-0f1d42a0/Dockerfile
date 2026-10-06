# Use official Node.js for frontend build
FROM node:18 AS frontend-builder
WORKDIR /app
COPY ./frontend/package*.json ./frontend/yarn.lock* ./frontend/
RUN yarn install --frozen-lockfile
COPY ./frontend/ ./frontend/
WORKDIR /app/frontend
RUN yarn build

# Use official Python image for backend
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY ./backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source
COPY ./backend ./backend

# Copy frontend build to static directory inside backend
RUN mkdir -p ./backend/static
COPY --from=frontend-builder /app/frontend/build ./backend/static

WORKDIR /app/backend

EXPOSE 8080

# Use uvicorn as the server on 0.0.0.0:8080
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
