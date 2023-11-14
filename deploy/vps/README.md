# VPS deployment

The files in this directory let you deploy winget.pro to a Linux VPS. They are
tested on stock Debian 11 but should also run on other Linux distributions such
as Ubuntu with modifications.

To deploy winget.pro to a Debian 11 server, upload
[`install.sh`](install.sh) and a `.bashrc` file with the settings below to the
server, then run `install.sh` as root.

```bash
# Set DEBUG to False in production:
export DEBUG=False

# The domain under which this server runs:
export HOST_NAME=some.domain.com

# A space-separated list of alternative host names:
export ALT_HOST_NAMES=

export DJANGO_SECRET_KEY=atLeast50RandomChars

##### Optional settings for checking out the server source code with git #######

# The server that hosts this repository:
export GIT_SERVER=github.com
# The path on GIT_SERVER where this repository lies:
export GIT_REPO_NAME=omaha-consulting/winget.pro
# The branch of this repository that should be checked out:
export GIT_REPO_BRANCH=main
# The SSH public key for fetching this repository from GIT_SERVER:
export GIT_REPO_PUBKEY="ssh-rsa ... user@machine"
# The SSH private key for fetching this repository from GIT_SERVER.
# "\n"s separate lines:
export GIT_REPO_PRIVKEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"

############## Optional settings for sending server health emails ##############

# Email address of server administrator:
export ADMIN_EMAIL=email@example.com
# Emails to the admin will be sent via this account:
export SMTP_HOST=email-smtp.eu-central-1.amazonaws.com
export SMTP_USER=ABC123...
export SMTP_PASSWORD=aBc1234...
export SMTP_FROM=server@email.com

################## Optional settings for storing files on S3 ###################

export DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
export AWS_STORAGE_BUCKET_NAME=mybucket
export AWS_ACCESS_KEY_ID=ABC....
export AWS_SECRET_ACCESS_KEY=XYZ...
# Optionally set the access policy for uploaded files. The default is "private".
# Even with "private", update clients receive access to the files via presigned
# S3 URLs. Note however that the associated requests to S3 incur a performance
# overhead. To avoid it, set AWS_S3_CUSTOM_DOMAIN below.
export AWS_DEFAULT_ACL=public-read
# Optionally supply a CDN domain. You can set this to <bucket>.s3.amazonaws.com
# to avoid the performance overhead of presigned URLs. This requires that the
# files in the bucket are publicly readable. For example, via
# AWS_DEFAULT_ACL=public-read.
export AWS_S3_CUSTOM_DOMAIN=cdn.winget.pro
# To use a non-AWS S3 endpoint such as Linode, you can optionally set:
export AWS_S3_HOST=us-east-1.linodeobjects.com
# Optionally configure the proxy for S3 access:
export AWS_S3_PROXIES="{'http': 'foo.bar:3128', 'http://hostname': 'foo.bar:4012'}"

######### Optional settings for using a pre-generated SSL certificate ##########

# The full certificate chain with multiple BEGIN / END CERTIFICATE blocks:
export SSL_CERTIFICATE="-----BEGIN CERTIFICATE-----\n..."
# The certificate private key.
export SSL_CERTIFICATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
```