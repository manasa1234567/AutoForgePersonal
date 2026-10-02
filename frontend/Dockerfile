# ---- Stage 1: build Angular from the workspace root ----
FROM node:22-alpine AS build
WORKDIR /app

# Root manifests first (layer caching)
COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/package.json
# If you have other workspaces, add their package.json here, e.g.:
# COPY libs/shared/package.json ./libs/shared/package.json

RUN npm ci

# Now the source
COPY frontend ./frontend

# Build via the workspace; ng is resolved from the root node_modules
RUN npm run build -w frontend -- --configuration production

# ---- Stage 2: serve with nginx ----
FROM nginx:1.27-alpine
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template
# Wildcard matches frontend/dist/<project-name>/browser
COPY --from=build /app/frontend/dist/*/browser /usr/share/nginx/html
ENV BACKEND_URL=http://backend:8000
EXPOSE 80