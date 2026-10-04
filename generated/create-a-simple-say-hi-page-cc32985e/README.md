# Say Hi App

This is a simple React application that shows a single page displaying the text "Hi".

## Features
- Displays "Hi" prominently in the center of the page
- Responsive and accessible
- Runs in modern browsers with no plugins
- Served from a lightweight NGINX Docker container on port 8080

## Development

### Install dependencies

```bash
npm install
```

### Run locally

```bash
npm start
```

### Run tests

```bash
npm test
```

### Build production

```bash
npm run build
```

## Deployment

Build and run the Docker container:

```bash
docker build -t say-hi-app .
docker run -p 8080:8080 say-hi-app
```

Open http://localhost:8080 in your web browser. You should see the page with the text "Hi".

## Notes

- No backend or database is required for this application.
- The page serves HTTP on port 8080 inside the container. Deployment environments can add HTTPS termination externally.
- The page is tested to load correctly on modern browsers such as Chrome, Firefox, Edge, and Safari.
