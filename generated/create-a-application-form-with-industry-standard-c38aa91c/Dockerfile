# Use official node LTS & python base images

# Build frontend
FROM node:18 as frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.11-slim
WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

# Copy frontend build to backend static directory
COPY --from=frontend-build /app/frontend/build /app/backend/static

EXPOSE 8080

# Command to run backend with uvicorn listening to 0.0.0.0:8080
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
