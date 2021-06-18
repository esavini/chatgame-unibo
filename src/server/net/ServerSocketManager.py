import thread

from src.common.net.SocketManager import SocketManager


class ServerSocketManager(SocketManager):
    """Server side specific implementation of the socket manager."""

    MAX_CONNECTIONS = 10

    def __init__(self):
        super().__init__()

    def spawn_client_manager(self, manager):
        "# self.__socket."
        thread.start_new_thread(manager, self.__socket)

    def start_listening(self):
        """Start the server listening for new connections."""
        self.__socket.listen()

    def broadcast(self):
        """Broadcast to all clients a message."""

    def send(self, client):
        self.__socket.send()
