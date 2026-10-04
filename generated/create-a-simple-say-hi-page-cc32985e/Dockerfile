# Base image with Node.js for frontend build
FROM node:18-alpine as build-stage
WORKDIR /app

# Copy package manifests
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY ./src ./src
COPY tsconfig.json ./
COPY public ./public

# Build frontend static assets
RUN npm run build

# Production stage with a simple static server
FROM nginx:alpine

# Copy built static files from build stage
COPY --from=build-stage /app/build /usr/share/nginx/html

# Expose port 8080 for the service
EXPOSE 8080

# Configure nginx to listen on 8080 instead of default 80
RUN sed -i 's/listen       80;/listen       8080;/' /etc/nginx/conf.d/default.conf

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
