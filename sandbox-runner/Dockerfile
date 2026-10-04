FROM node:22-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv util-linux \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/runner-venv

ENV PATH="/opt/runner-venv/bin:${PATH}"
WORKDIR /opt/runner
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

RUN useradd --create-home --uid 10002 execuser \
    && chown -R root:root /opt/runner /opt/runner-venv
# The HTTP process stays root only so it can drop each untrusted check process
# to execuser. The child receives no cloud environment variables.
USER root

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--limit-max-requests", "100"]
