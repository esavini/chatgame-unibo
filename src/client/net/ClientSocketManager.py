from src.common.net.SocketManager import SocketManager


class ClientSocketManager(SocketManager):
    """A client specific implementation of the socket manager."""

    def connect(self, endpoint):
        """Connect to the specified endpoint."""
        self.__socket.connect(endpoint)

    def write(self, object):
        """Writes to the server a message."""

