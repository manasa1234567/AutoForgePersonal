# Application Form Fullstack

This is a fullstack application implementing a complete application form with an industry-standard layout including header and footer.

## Features

- React frontend with React Hook Form for validation and accessibility.
- FastAPI backend serving REST API endpoints.
- Backend serves static frontend build (via /static).
- Form includes typical personal, address, and job application fields plus resume upload.
- Responsive and accessible design.
- Containerized via Docker for easy deployment.

## Development

### Frontend

From `frontend` directory:

```bash
npm install
npm run dev
```

The frontend dev server proxies API calls to backend.

### Backend

From `backend` directory:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deployment

Build and run the image with Docker:

```bash
docker build -t application-form-fullstack .
docker run -p 8080:8080 application-form-fullstack
```

Access the app at `http://localhost:8080/static/index.html` in browser.

## Notes

- No persistent data storage is implemented. Backend validates and confirms receipt only.
- Environment variables can be used for DB or storage configuration in future enhancements.
- User authentication is not implemented.

## License

MIT
