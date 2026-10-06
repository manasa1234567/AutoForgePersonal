FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements and install
COPY ./backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code
COPY ./backend ./backend

# Install frontend dependencies and build
WORKDIR /app/frontend
COPY ./frontend/package.json ./frontend/package-lock.json* ./
RUN npm install
COPY ./frontend ./
RUN npm run build

# Workdir back to /app
WORKDIR /app

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
