from src.common.net.SocketManager import SocketManager

sock = SocketManager()
sock.start_listening()
print(sock.get_ip_address())
