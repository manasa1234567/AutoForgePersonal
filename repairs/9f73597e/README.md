# Repair existing build 9f73597e

Target branch: `feature/create-a-application-form-with-industry-standard-9f73597e`.

Target project folder: `generated/create-a-application-form-with-industry-standard-9f73597e`.

Use GitHub's web editor (press `.` on that branch) to make all changes in one commit:

1. Replace the project's root `Dockerfile` with this folder's `Dockerfile`.
2. Add `autoforge_entry.py` at the project root using this folder's file.
3. Replace the project's `backend/requirements.txt` with this folder's `requirements.txt`.
4. In `backend/app/main.py`, change `constr(regex=` to `constr(pattern=`. The generated source uses the Pydantic 1 keyword, while requirements install Pydantic 2.
5. Commit these changes together on the existing feature branch. Its generated-app workflow runs automatically.

This reuses the existing generated source and requires no new agent generation.

The repair aligns frontend build paths, imports `backend.app.main`, installs runtime dependencies in the final image, and serves the frontend at `/` with the existing backend `/submit` route.

No live Docker build has been performed locally: Docker is unavailable. The workflow must build and start this image before deployment success is established.

Database persistence is not configured by this repair. Without `DATABASE_URL`, the existing `/submit` route returns HTTP 503. Configure the intended database and its Python driver separately; do not treat a successful homepage response as verification of form submission.
