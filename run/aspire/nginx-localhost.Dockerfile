# Stage 1: Handle SSL certificates using powershell
FROM mcr.microsoft.com/powershell:ubuntu-22.04 AS cert-generator
# Set build time args
ARG CERTIFICATE_NAME
ARG CERTIFICATE_DNS_NAME
ARG CERTIFICATE_PASSWORD

# Set environment variables from build-time arguments 
ENV CERTIFICATE_NAME=${CERTIFICATE_NAME}
ENV CERTIFICATE_DNS_NAME=${CERTIFICATE_DNS_NAME}
ENV CERTIFICATE_PASSWORD=${CERTIFICATE_PASSWORD}

COPY /run/aspire/generate_pem.ps1 /generate_pem.ps1
COPY /run/aspire/localhostssl /srv/nginx/certs

# Run the PowerShell script to create PEM file 
RUN pwsh -File /generate_pem.ps1 -CertificateName $CERTIFICATE_NAME -CertificatePassword $CERTIFICATE_PASSWORD


# Stage 2: Nginx with SSL configuration
FROM nginx:1.25.3

# Set build time args
ARG CERTIFICATE_NAME
ARG CERTIFICATE_DNS_NAME


# Set environment variables from build-time arguments 
ENV CERTIFICATE_NAME=${CERTIFICATE_NAME}
ENV CERTIFICATE_DNS_NAME=${CERTIFICATE_DNS_NAME}

# Copy the Nginx configuration file template
COPY run/aspire/nginx.conf.template /etc/nginx/nginx.conf.template

# Copy the generated SSL certificate and key from the previous stage
COPY --from=cert-generator /srv/nginx/certs /etc/nginx/certs
RUN ls /etc/nginx/certs


# Use envsubst to substitute environment variables in the Nginx configuration
RUN apt-get update && apt-get install -y gettext-base
CMD ["/bin/sh", "-c", "envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && cat /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]

# Expose ports for HTTP and HTTPS
EXPOSE 80 443
