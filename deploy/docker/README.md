# Running winget.pro via Docker

To run winget.pro with Docker, first uncomment the `DJANGO_SUPERUSER_...` lines
in [`docker-compose.yml`](docker-compose.yml) and edit them to set the
credentials of the user you want to log in with.

Then execute the following command:

    docker-compose up

You should now be able to log into the service at http://localhost:8000/admin
with the credentials you chose in the first step.

Before you run `docker-compose up` again, remove the `DJANGO_SUPERUSER_...`
lines from [`docker-compose.yml`](docker-compose.yml). Otherwise, the server
would attempt to create the initial user again.

`winget` requires repositories to run under `https://`. For production use, you
now need to set up a reverse proxy that accepts `https://` requests and forwards
them to `localhost:8000`. To test things on your local PC, you can use the
[SSL Proxy](../sslproxy) provided in this repository.