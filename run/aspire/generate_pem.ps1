# generate_pem.ps1
param (
    [Parameter(Mandatory = $true)][string]$CertificateName,
    [Parameter(Mandatory = $true)][string]$CertificatePassword
)

# Securely convert password
$passwordSecure = ConvertTo-SecureString -String $CertificatePassword -Force -AsPlainText

# Create PEM file from PFX
openssl pkcs12 -in "/srv/nginx/certs/$CertificateName.pfx" -out "/srv/nginx/certs/$CertificateName.pem" -nodes -password pass:$CertificatePassword

# Combine CRT and KEY into PEM
cat "/srv/nginx/certs/$CertificateName.crt" "/srv/nginx/certs/$CertificateName.key" >> "/srv/nginx/certs/$CertificateName.pem"
