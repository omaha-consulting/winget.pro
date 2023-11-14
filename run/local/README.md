# Running winget.pro on your own computer

Running winget.pro locally (that is, on the same PC where `winget` commands are
then used to install software) is mostly done during development. For production
use, consider one of the other deployment options.

## Set up the development environment

    pip install -Ur requirements/base-full.txt

## Initialise the database

1. Run `python manage.py migrate`
2. Run `python manage.py createsuperuser`
3. Run `python manage.py runserver`
4. Log into `/admin` and follow the instructions to create a _Tenant_.

## Start the server

Execute the following command if it is not still running:

    python manage.py runserver

This starts to server on `http://localhost:8000`. `winget` however requires the
server to accept `https://` requests. This can be done during development with
the SSL proxy from this repository.  Please see the
[`sslproxy/` directory](../sslproxy) for instructions. Typically, you will
run the following command:

    python sslproxy.py

Now you can add a REST source in winget (note the `httpS`):

    winget source add -n dev -a https://localhost:8443/ab... -t "Microsoft.Rest"

Here, `ab...` is the UUID of the Tenant.

You can perform queries against the new source. Eg.:

    winget search "search term" -s dev

# Sniffing Microsoft's implementation

Microsoft's implementation is the `msstore` source shown in
`winget source list`. Typically, it runs under:

    https://storeedgefd.dsx.mp.microsoft.com/v9.0

To sniff it, the easiest way is to use a network inspection tool such as Fiddler
Classic. This however uses its own SSL certificate, which `winget` rejects. To
work around this, set the REG_DWORD registry value
`HKLM\SOFTWARE\Policies\Microsoft\Windows\AppInstaller\EnableBypassCertificatePinningForMicrosoftStore`
to `1`.