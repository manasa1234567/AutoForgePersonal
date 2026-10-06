# Application Form Backend

This FastAPI backend provides an API for submitting a complete application form.

Setup:
- Create a virtual environment.
- Run `pip install -r requirements.txt`.
- Start the server with:

  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

The backend currently uses in-memory validation and simulates submission without a database.

Root endpoint is `/` returning 200 OK.

Submit application data via POST to `/submit` endpoint with JSON body matching the form fields.
