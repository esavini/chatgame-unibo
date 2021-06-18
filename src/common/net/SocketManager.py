import socket


class SocketManager:
    """A class that helps managing the socket."""

    LISTENING_PORT = 55123
    """The port of the server."""

    __LOCALHOST = '127.0.0.1'

    def __init__(self):
        """Creates a new instance of the socket manager."""
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(('', self.LISTENING_PORT))  # Binding to '' is the same of '0.0.0.0' (all routes)

    def stop(self):
        """Stops the server listening."""
        self.__socket.close()

    def get_ip_address(self):
        """Returns the current IP address of the server."""
        try:
            return self.__socket.getsockname()[0]
        except OSError:
            return self.__LOCALHOST
