# Stage 1: Generate SSL certificate using PowerShell
FROM mcr.microsoft.com/powershell:ubuntu-22.04 AS cert-generator

# define build-time arguments
ARG CERTIFICATE_NAME
ARG CERTIFICATE_PASSWORD
ARG CERTIFICATE_SUBJECT
ARG CERTIFICATE_DNS_NAME

# Set environment variables from build-time arguments 
ENV CERTIFICATE_NAME=${CERTIFICATE_NAME} 
ENV CERTIFICATE_PASSWORD=${CERTIFICATE_PASSWORD}
ENV CERTIFICATE_SUBJECT=${CERTIFICATE_SUBJECT}
ENV CERTIFICATE_DNS_NAME=${CERTIFICATE_DNS_NAME}

# Copy the PowerShell script to the container
COPY run/aspire/certificate_setup.ps1 /certificate_setup.ps1

# Ensure the certs directory exists
RUN mkdir -p /srv/nginx/certs

# Run the PowerShell script to generate the certificate
RUN pwsh /certificate_setup.ps1 -certificatename $CERTIFICATE_NAME -certificatepassword $CERTIFICATE_PASSWORD -subject $CERTIFICATE_SUBJECT -dnsName $CERTIFICATE_DNS_NAME

# Stage 2: Nginx with SSL configuration
FROM nginx:1.25.3

# define build-time arguments
ARG CERTIFICATE_NAME
ARG CERTIFICATE_PASSWORD
ARG CERTIFICATE_SUBJECT
ARG CERTIFICATE_DNS_NAME
ARG SECURE_PORT

# Set environment variables from build-time arguments 
ENV CERTIFICATE_NAME=${CERTIFICATE_NAME} 
ENV CERTIFICATE_PASSWORD=${CERTIFICATE_PASSWORD}
ENV CERTIFICATE_SUBJECT=${CERTIFICATE_SUBJECT}
ENV CERTIFICATE_DNS_NAME=${CERTIFICATE_DNS_NAME}
ENV SECURE_PORT=${SECURE_PORT}

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
