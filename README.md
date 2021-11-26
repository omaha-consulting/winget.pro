# winget private repository

A Python implementation of a private winget repository server (/REST API).

## Setting up a local SSL certificate

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

### Run locally

    python manage.py runserver

Then:

    python sslproxy.py

Then you can open `https://localhost:8443` in the browser.