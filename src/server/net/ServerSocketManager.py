import threading

from src.common.net.SocketManager import SocketManager

class ServerSocketManager(SocketManager):
    """Server side specific implementation of the socket manager."""

    def __init__(self):
        super().__init__()
        self.thread = None

    def start_client_manager(self, manager):
        """Handles incoming connections."""
        self.thread = threading.Thread(target=manager, args=(self.__socket,))
        self.thread.start()

    def start_listening(self):
        """Start the server listening for new connections."""
        self.__socket.listen()
