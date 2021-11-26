import socket, ssl

from threading import Thread

def forward(source, destination):
    string = b' '
    while string:
        string = source.recv(1024)
        if string:
            destination.sendall(string)
        else:
            source.shutdown(socket.SHUT_RD)
            destination.shutdown(socket.SHUT_WR)

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="conf/localhost.cert", keyfile="conf/localhost.key")

bindsocket = socket.socket()
bindsocket.bind(('', 8443))
bindsocket.listen(5)

print("Forwarding https://localhost:8443 -> http://localhost:8000")

while True:
    try:
        newsocket, fromaddr = bindsocket.accept()
        client_socket = context.wrap_socket(newsocket, server_side=True)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(('localhost', 8000))
        Thread(target=forward, args=(client_socket, server_socket)).start()
        Thread(target=forward, args=(server_socket, client_socket)).start()
    except KeyboardInterrupt:
        break