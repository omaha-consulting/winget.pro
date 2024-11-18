# VPS deployment

The files in this directory let you deploy winget.pro to a Linux VPS. They are
tested on stock Debian 12 but should also run on other Linux distributions such
as Ubuntu with modifications.

To deploy winget.pro to a Debian 12 server, upload
[`install.sh`](install.sh) and a `.bashrc` file with the settings below to the
server, then run `install.sh` as root.

```bash
# Set DEBUG to False in production:
export DEBUG=False

# The domain under which this server runs:
export HOST_NAME=your.domain.com

export DJANGO_SECRET_KEY=atLeast50RandomChars

# Fetch the server source code from GitHub:
export GIT_SERVER=github.com

# Email address of the server administrator. Receives server health emails.
export ADMIN_EMAIL=email@gmail.com
```

After you have run the install script for the first time, you then also need to
create a superuser for logging in:

```bash
su -c '/srv/manage.py createsuperuser' - django
```

Now you can log in at `https://your.domain.com/admin/`.

## Optional settings

You can add additional lines to `.bashrc` to customize the server setup. This
needs to be done when you set up the server. It cannot be done later.

### Multiple domains

```bash
export ALT_HOST_NAMES="first.domain.com second.domain.com"
```

### Checkout of the server source code

With `GIT_SERVER=github.com`, `install.sh` checks out the public implementation
from GitHub. You can omit `GIT_SERVER` if your server does not have internet
access and you want to upload the source code into `/srv` yourself.

When `GIT_SERVER` is set, you can use the following settings to customize the
checkout:

```bash
# The path on GIT_SERVER where this repository lies:
export GIT_REPO_NAME=omaha-consulting/winget.pro

# The branch of this repository that should be checked out:
export GIT_REPO_BRANCH=main
```

By default, the checkout is performed via `https://`. If you want to do it with
authentication as the user `git`, which is typical for private repositories,
then you can add the following:

```bash
# The SSH public key for fetching this repository from GIT_SERVER:
export GIT_REPO_PUBKEY="ssh-rsa ... user@machine"
# The SSH private key for fetching this repository from GIT_SERVER.
# "\n"s separate lines:
export GIT_REPO_PRIVKEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
```

### Using a pre-generated SSL certificate

By default, `install.sh` generates an SSL certificate for the server using
LetsEncrypt. If this is not possible in your environment, for example because
you are hosting on a private domain that is not reachable from the public
internet, then you can use the following settings to supply your own SSL
certificate:

```bashrc
# The full certificate chain with multiple BEGIN / END CERTIFICATE blocks:
export SSL_CERTIFICATE="-----BEGIN CERTIFICATE-----\n..."
# The certificate private key.
export SSL_CERTIFICATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
```

### Server health emails

These settings let the server send health emails to `ADMIN_EMAIL` above:

```bashrc
export SMTP_HOST=email-smtp.eu-central-1.amazonaws.com
export SMTP_USER=ABC123...
export SMTP_PASSWORD=aBc1234...
export SMTP_FROM=server@email.com
```

### Storing files on S3

By default, uploaded files are stored on the server. You can store them on
S3-compatible storage platforms instead via the following settings:

```bashrc
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
```