FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies based on package.json and lockfile
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY . .

# Build app
RUN npm run build

# Production stage
FROM nginx:stable-alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Replace default nginx.conf with configuration to listen on port 8080
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 (mapped by container hosting)
EXPOSE 8080

# Start nginx server
CMD ["nginx", "-g", "daemon off;"]
