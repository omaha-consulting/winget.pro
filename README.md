# api.winget.pro

A Python implementation of a private winget repository server (/REST API).

## Running locallly

### Install a local SSL certificate

`winget` only allows `https://` sources. This means that if we want to run
locally, then we need a self-signed SSL certificate for `localhost`.

[`localhost.pfx`](conf/localhost.pfx) can be used for this purpose. It was
created from [these instructions](https://gist.github.com/alicoskun/57acda07d5ab672a3c820da57b9531e3).
To install it, issue the following in a Powershell Admin prompt:

```bash
$password=ConvertTo-SecureString "12345" -asplaintext -force
Import-PfxCertificate -FilePath conf\localhost.pfx Cert:\LocalMachine\My -Password $password -Exportable
Import-Certificate -FilePath conf\localhost.cert -CertStoreLocation Cert:\CurrentUser\Root
```

To remove it later, run `mmc`, click `File/Add or Remove Snap-in` then
`Certificates/Add/My User account` then `Finish` and again for
`Computer account`. Then click `OK`. Then delete `localhost` expiring 2041 from
`Current User/Personal`, `Current User/Trusted Root Certification Authorities`,
and `Local Computer/Personal`.

### Set up the development environment

    pip install -Ur requirements/base-full.txt

### Initialise the database

1. Run `python manage.py migrate`
2. Run `python manage.py createsuperuser`
3. Run `python manage.py runserver`
4. Log into `/admin` and create a _Tenant_.

### Run locally

    python manage.py runserver

Then:

    python sslproxy.py

Then you can add the REST source (note the `httpS`):

    winget source add -n dev -a https://localhost:8443/ab... -t "Microsoft.Rest"

Here, `ab...` is the UUID of the Tenant.

Then you can perform queries against the new source. Eg.:

    winget search "search term" -s dev

## Sniffing Microsoft's implementation

Microsoft's implementation is the `msstore` source shown in
`winget source list`. Typically, it runs under:

    https://storeedgefd.dsx.mp.microsoft.com/v9.0

To sniff it, the easiest way is to use a network inspection tool such as Fiddler
Classic. This however uses its own SSL certificate, which `winget` rejects. To
work around this, set the REG_DWORD registry value
`HKLM\SOFTWARE\Policies\Microsoft\Windows\AppInstaller\EnableBypassCertificatePinningForMicrosoftStore`
to `1`.

## Deploying

Upload [`install.sh`](install.sh) and a `.bashrc` file with the settings below
to a Debian 11 server, then run `install.sh` as root.

```bash
# Email address of server administrator:
export ADMIN_EMAIL=email@example.com

# The domain under which this server runs:
export HOST_NAME=some.domain.com

# A space-separated list of alternative host names:
export ALT_HOST_NAMES=

# The server that hosts this repository:
export GIT_SERVER=github.com

# The path on GIT_SERVER where this repository lies:
export GIT_REPO_NAME=omaha-consulting/api.winget.pro

# The branch of this repository that should be checked out:
export GIT_REPO_BRANCH=main

# The SSH public key for fetching this repository from GIT_SERVER:
export GIT_REPO_PUBKEY="ssh-rsa ... user@machine"

# The SSH private key for fetching this repository from GIT_SERVER.
# "\n"s separate lines:
export GIT_REPO_PRIVKEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"

# Emails to the admin will be sent via this account:
export SMTP_HOST=email-smtp.eu-central-1.amazonaws.com
export SMTP_USER=ABC123...
export SMTP_PASSWORD=aBc1234...
export SMTP_FROM=server@email.com

# Django SECRET_KEY:
export SECRET_KEY=atLeast50RandomChars

DJANGO_SETTINGS_MODULE=core.settings

################## Optional settings for storing files on S3 ###################
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
AWS_STORAGE_BUCKET_NAME=mybucket
AWS_ACCESS_KEY_ID=ABC....
AWS_SECRET_ACCESS_KEY=XYZ...
# Optionally set the access policy for uploaded files. The default is "private".
# Even with "private", update clients receive access to the files via presigned
# S3 URLs. Note however that the associated requests to S3 incur a performance
# overhead. To avoid it, set AWS_S3_CUSTOM_DOMAIN below.
AWS_DEFAULT_ACL=public-read
# Optionally supply a CDN domain. You can set this to <bucket>.s3.amazonaws.com
# to avoid the performance overhead of presigned URLs. This requires that the
# files in the bucket are publicly readable. For example, via
# AWS_DEFAULT_ACL=public-read. 
AWS_S3_CUSTOM_DOMAIN=cdn.winget.pro
# To use a non-AWS S3 endpoint, you can optionally set the following:
AWS_S3_HOST=us-east-1.linodeobjects.com
```