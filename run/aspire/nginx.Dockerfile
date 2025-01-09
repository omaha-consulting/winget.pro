# Stage 1: Nginx with SSL configuration
FROM nginx:1.25.3

# define build-time arguments
ARG CERTIFICATE_NAME
ARG CERTIFICATE_PASSWORD
ARG CERTIFICATE_SUBJECT
ARG CERTIFICATE_DNS_NAME
ARG CERTIFICATE_EMAIL
ARG SECURE_PORT

# Set environment variables from build-time arguments 
ENV CERTIFICATE_NAME=${CERTIFICATE_NAME} 
ENV CERTIFICATE_PASSWORD=${CERTIFICATE_PASSWORD}
ENV CERTIFICATE_SUBJECT=${CERTIFICATE_SUBJECT}
ENV CERTIFICATE_DNS_NAME=${CERTIFICATE_DNS_NAME}
ENV CERTIFICATE_EMAIL=${CERTIFICATE_EMAIL}
ENV SECURE_PORT=${SECURE_PORT}

# Copy the Nginx configuration file template
COPY run/aspire/nginx.conf.template /etc/nginx/nginx.conf.template

# Use certibot to generate ssl certificate. The two lines bellow can be configured to use a purchased certificate instead of generating one
RUN apt-get update -y && apt-get install python3-certbot-nginx -y
RUN certbot certonly --nginx --non-interactive --agree-tos --domains ${CERTIFICATE_DNS_NAME} --rsa-key-size 4096 --keep-until-expiring --expand --cert-name ${CERTIFICATE_NAME} --email ${CERTIFICATE_EMAIL} --renew-by-default --no-eff-email --force-renewal

# Use envsubst to substitute environment variables in the Nginx configuration
RUN apt-get update && apt-get install -y gettext-base
CMD ["/bin/sh", "-c", "envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && cat /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]

# Expose ports for HTTP and HTTPS
EXPOSE 80 443
