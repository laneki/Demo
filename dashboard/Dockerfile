FROM nginx:1.27-alpine
COPY dashboard/index.html /usr/share/nginx/html/index.html
COPY dashboard/styles.css /usr/share/nginx/html/styles.css
COPY dashboard/app.js /usr/share/nginx/html/app.js
COPY dashboard/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
