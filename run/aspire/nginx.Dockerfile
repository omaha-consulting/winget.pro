FROM nginx:1.25.3
COPY run/aspire/nginx.conf /etc/nginx
EXPOSE 80