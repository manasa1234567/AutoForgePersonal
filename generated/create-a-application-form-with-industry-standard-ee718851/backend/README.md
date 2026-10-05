# Backend API

FastAPI application for handling application form submissions.

## Running

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /`: Health check.
- `POST /api/applications`: Submit application form JSON.

## Notes

- Currently stores data in memory. Replace with DB persistence as needed.
