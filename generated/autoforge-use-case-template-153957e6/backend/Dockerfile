FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy source
COPY ./app ./app
COPY ./requirements.txt ./

# Install dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8080

# Start Uvicorn server
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]
