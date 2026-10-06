FROM node:22-alpine AS build
WORKDIR /src
COPY frontend/. .
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi \
    && npm run build \
    && output="$(find dist build -type f -name index.html 2>/dev/null | head -n 1)" \
    && test -n "$output" \
    && mkdir -p /site \
    && cp -a "$(dirname "$output")"/. /site/
FROM nginx:1.27-alpine
COPY --from=build /site/ /usr/share/nginx/html/
RUN printf 'server {\n  listen 8080;\n  server_name _;\n  root /usr/share/nginx/html;\n  index index.html;\n  location / { try_files $uri $uri/ /index.html; }\n}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 8080
