# Use official Node.js LTS image
FROM node:18.16.1-alpine3.18

# Set working directory
WORKDIR /app

# Copy package manifests
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build the React app
RUN npm run build

# Use a lightweight web server to serve the build - using 'serve' package
RUN npm install -g serve

# Expose port
EXPOSE 8080

# Run serve on the build folder
CMD ["serve", "-s", "build", "-l", "8080"]
