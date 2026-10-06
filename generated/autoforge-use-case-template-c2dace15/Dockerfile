FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
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

# Move backend workdir back
WORKDIR /app

# Expose port
EXPOSE 8080

# Start the FastAPI app with uvicorn
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
