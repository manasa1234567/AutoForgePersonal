# Start from official Node image
FROM node:20-alpine3.18 AS build

# Set working directory inside container
WORKDIR /app

# Copy package.json and dev dependencies files
COPY package.json .
COPY vite.config.ts .
COPY tsconfig.json .

# Copy source files
COPY src ./src

# Install dependencies
RUN npm install

# Build production bundle
RUN npm run build

# Production image
FROM nginx:stable-alpine

# Copy built frontend assets
COPY --from=build /app/dist /usr/share/nginx/html

# Replace default nginx.conf with custom config to listen on 8080
RUN mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak && \
    echo 'user  nginx;\nworker_processes  1;\nevents { worker_connections 1024; }\nhttp {\n  include /etc/nginx/mime.types;\n  default_type application/octet-stream;\n  sendfile on;\n  keepalive_timeout 65;\n  server {\n    listen 8080 default_server;\n    listen [::]:8080 default_server;\n    root /usr/share/nginx/html;\n    index index.html;\n    location / {\n      try_files $uri /index.html;\n    }\n  }\n}\n' > /etc/nginx/nginx.conf

# Expose port 8080
EXPOSE 8080

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
