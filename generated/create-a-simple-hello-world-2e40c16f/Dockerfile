# Build stage
FROM node:18-alpine as build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
