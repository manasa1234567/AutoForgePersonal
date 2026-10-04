FROM nginx:alpine

# Remove default nginx welcome page
RUN rm /usr/share/nginx/html/*

# Copy our static index.html
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 8080

# Configure nginx to listen on port 8080 (instead of default 80)
RUN sed -i 's/listen       80;/listen       8080;/g' /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
