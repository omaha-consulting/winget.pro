"""
Usage:

    python sslproxy [local_port] [dest_host] [dest_port]

The defaults are local_port=8443, dest_host=localhost, dest_port=8000.
"""

import socket, ssl, sys

from functools import partial
from threading import Thread

if len(sys.argv) > 1:
    local_port = int(sys.argv[1])
else:
    local_port = 8443

if len(sys.argv) > 2:
    dest_host = sys.argv[2]
else:
    dest_host = 'localhost'

if len(sys.argv) > 3:
    dest_port = int(sys.argv[3])
else:
    dest_port = 8000

def forward(source, destination, prefix=''):
    data = b' '
    while data:
        try:
            data = source.recv(1024)
            if data:
                try:
                    decoded = data.decode('utf-8')
                except UnicodeDecodeError:
                    destination.sendall(data)
                else:
                    for line in decoded.split('\n'):
                        print(prefix + line)
                    decoded = decoded.replace(
                        f'\nHost: localhost:{local_port}',
                        f'\nHost: {dest_host}:{dest_port}'
                    )
                    destination.sendall(decoded.encode('utf-8'))
            else:
                source.shutdown(socket.SHUT_RD)
                destination.shutdown(socket.SHUT_WR)
        except ConnectionResetError:
            break

local_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
local_context.load_cert_chain(
    certfile="localhost.cert", keyfile="localhost.key"
)

if dest_port == 443:
    dest_context = ssl.create_default_context()
else:
    dest_context = None

bindsocket = socket.socket()
bindsocket.bind(('', local_port))
bindsocket.listen(5)
bindsocket.settimeout(.5)

print(f'Forwarding localhost:{local_port} -> {dest_host}:{dest_port}')

while True:
    try:
        try:
            newsocket, fromaddr = bindsocket.accept()
            client = local_context.wrap_socket(newsocket, server_side=True)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((dest_host, dest_port))
            if dest_context:
                server = dest_context.wrap_socket(server, server_hostname=dest_host)
            Thread(
                target=partial(forward, prefix='-> '), args=(client, server)
            ).start()
            Thread(
                target=partial(forward, prefix='<- '), args=(server, client)
            ).start()
        except socket.timeout:
            pass
    except KeyboardInterrupt:
        break
