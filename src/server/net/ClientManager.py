import json
import threading
from socket import socket


class ClientManager:
    """An implementation of a client manager."""

    BUFFER_SIZE = 2048
    """The size of the buffer."""

    def __init__(self):
        self.clients = []
        self.stopped = False

    def handle_incoming(self, socket: socket):
        while not self.stopped:
            client, addr = socket.accept()

            print("Incoming connection from %s", addr)

            self.clients.append(client)
            thread = threading.Thread(target=self.handle_client,
                                      args=(client, len(self.clients) - 1,))
            thread.start()

    def handle_client(self, client: socket, index):
        """"""
        message = bytearray()

        while not self.stopped and self.clients[index] is not None:
            try:
                data = client.recv(self.BUFFER_SIZE)

                if data:
                    message.extend(data)

                if message.endswith(bytes(0x00)):
                   "ToDo"

            except:
                self.clients[index] = None

    def broadcast(self, obj):
        """Sends a broadcast all clients."""
        serialized_data = json.dumps(obj)

        for i, client in enumerate(self.clients):
            if client is not None:
                try:
                    client.send(bytes(serialized_data))

                except OSError:
                    # When the communication throws an exception
                    # we set the client to none to declare that is closed
                    self.clients[i] = None

    def stop(self):
        for client in self.clients:
            if client is not None:
                client.close()
