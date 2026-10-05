FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
COPY autoforge_entry.py ./autoforge_entry.py
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "autoforge_entry:app", "--host", "0.0.0.0", "--port", "8080"]
