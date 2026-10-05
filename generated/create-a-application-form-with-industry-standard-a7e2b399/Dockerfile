# Build stage for frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build stage for backend
FROM python:3.11-slim AS backend-build
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend

# Final image stage
FROM python:3.11-slim
WORKDIR /app
# Copy backend code
COPY --from=backend-build /app/backend ./backend
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Copy frontend build output to serve static
COPY --from=frontend-build /app/build ./frontend/build

EXPOSE 8080

ENV PYTHONPATH=/app/backend

# Start both backend (uvicorn) and a simple static file server for frontend
# Use a tiny node static server (serve) is common but we want to avoid node in final image
# Use 'uvicorn' to serve API on port 8000 and reverse proxy through uvicorn's root

# However, for simplicity, we will serve frontend static files on / via fastapi static files mount
# and backend API on /submit

# Create a startup script:
RUN echo """
#!/bin/sh
uvicorn backend.main:app --host 0.0.0.0 --port 8080
""" > /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
