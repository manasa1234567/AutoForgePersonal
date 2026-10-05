# --- Backend stage ---
FROM python:3.11-slim as backend-build

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# --- Frontend stage ---
FROM node:18-alpine as frontend-build

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./frontend/
RUN npm run build

# --- Final stage ---
FROM python:3.11-slim

WORKDIR /app

COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build output
COPY --from=frontend-build /app/frontend/build /app/frontend/build

# Install uvicorn
RUN pip install --no-cache-dir uvicorn[standard]==0.34.2

# Expose port 8080
EXPOSE 8080

# Start uvicorn to serve backend and static frontend via mount
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
