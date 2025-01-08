param (
    [Parameter(Mandatory = $true)][string]$certificateName,
    [Parameter(Mandatory = $true)][string]$certificatePassword,
    [Parameter(Mandatory = $true)][string]$subject,
    [Parameter(Mandatory = $true)][string]$dnsName
)

# Create certificates directory
$certsDir = "/srv/nginx/certs"
if (!(Test-Path $certsDir)) {
    New-Item -ItemType Directory -Force -Path $certsDir
}

# Paths for certificate and key files
$certPath = "$certsDir/$certificatename.crt"
$keyPath = "$certsDir/$certificatename.key"
$pemPath = "$certsDir/$certificatename.pem"

# Generate self-signed certificate using OpenSSL (Linux)
# Construct the OpenSSL command 
$opensslCommand = @"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$keyPath" -out "$certPath" -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=$dnsName"
"@
Write-Host $opensslCommand
Invoke-Expression $opensslCommand

# Combine certificate and key into PEM file
$combineCommand = "cat $keyPath $certPath > $pemPath"
Invoke-Expression $combineCommand

# List the contents of the certs directory for debugging
Get-ChildItem -Path $certsDir
