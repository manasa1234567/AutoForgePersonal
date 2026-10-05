# Repair build a989645f without generating again

The log fails because @vitejs/plugin-react 4.0.9 is not published. The replacement
4.0.4 is published and supports the project's Vite 4.4.9. The original Dockerfile
also omits index.html from its build stage; both issues are corrected here.

1. Open GitHub repository manasa1234567/AutoForgePersonal.
2. Select branch `feature/create-a-application-form-with-industry-standard-a989645f`.
3. Press `.` to open GitHub's web editor so both changes can be committed together.
4. Open `generated/create-a-application-form-with-industry-standard-a989645f/`.
5. Replace its `package.json` and `Dockerfile` with the adjacent repair files,
   and add the adjacent `package-lock.json` in that same generated folder.
6. Commit all three files together to that feature branch. This triggers deployment.

Do not just re-run the old failed job: it uses the old commit. Pushing the
normalizer change to main helps future generations but does not repair this
existing feature branch.

This generated project has no backend or database: form submission only changes
local UI state. Packaging corrections do not add persistence.

Docker is unavailable in the local workspace; GitHub must still verify the
complete image and Azure deployment. No changes have been pushed automatically.
The corrected manifest resolved successfully with npm using
`install --package-lock-only --ignore-scripts`; the repair image uses `npm ci`
with that lockfile. Compilation and container startup remain unverified locally.
