# Use official Node.js 18 image for frontend build
FROM node:18 as frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Use official Python 3.11 image for backend
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend

# Install backend dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build output to serve statically
COPY --from=frontend-build /app/frontend/build /app/backend/static

# Install and run uvicorn for FastAPI
EXPOSE 8080

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--root-path", "", "--static-dir", "static"]
