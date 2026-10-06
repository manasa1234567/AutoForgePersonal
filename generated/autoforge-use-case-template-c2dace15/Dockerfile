FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY ./backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code
COPY ./backend ./backend

# Install NodeJS for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy frontend package.json and package-lock.json
COPY ./frontend/package.json ./frontend/package-lock.json* ./frontend/

# Install frontend dependencies and build
WORKDIR /app/frontend
RUN npm install
COPY ./frontend ./
RUN npm run build

# Move frontend build to backend static directory
RUN mkdir -p /app/backend/app/static && cp -r ./build/* /app/backend/app/static/

# Set working directory back to backend
WORKDIR /app

EXPOSE 8080

# Start backend API
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
