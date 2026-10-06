FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests
COPY requirements.txt ./

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY ./app ./app

# Expose port
EXPOSE 8080

ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8080

# Run the FastAPI application using uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
