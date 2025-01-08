# SSL Proxy

`winget` only allows `https://` sources. In production, you will have a web
server such as Nginx that accepts `https://` requests and forwards them to the
winget.pro Python server.

The files in this directory provide a mini web server that can accept https://
requests and forwards them to a winget.pro instance that does not support
https://. This is useful for development and testing.

## Install the self-signed SSL certificate

The implementation here requires us to have a self-signed SSL certificate for
`localhost`. [`localhost.pfx`](../sslproxy/localhost.pfx) can be used for this
purpose. It was created from
[these instructions](https://gist.github.com/alicoskun/57acda07d5ab672a3c820da57b9531e3).
To install it, issue the following in a Powershell Admin prompt:

```bash
$password=ConvertTo-SecureString "12345" -asplaintext -force
Import-PfxCertificate -FilePath localhost.pfx Cert:\LocalMachine\My -Password $password -Exportable
Import-Certificate -FilePath localhost.cert -CertStoreLocation Cert:\CurrentUser\Root
```

To remove it later, run `mmc`, click `File/Add or Remove Snap-in` then
`Certificates/Add/My User account` then `Finish` and again for
`Computer account`. Then click `OK`. Then delete `localhost` expiring 2041 from
`Current User/Personal`, `Current User/Trusted Root Certification Authorities`,
and `Local Computer/Personal`.

## Run the aspire application

Once you have installed the self-signed SSL certificate above, you can run the
following command to start the aspire application locally

```dotnetcli

dotnet run --project aspire/aspire.csproj

````
