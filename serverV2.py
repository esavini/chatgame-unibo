import json
import socket
import threading
import tkinter as tk


class Client:
    def __init__(self, socket, ip):
        self.socket = socket
        self.ip = ip
        self.username = None

    def set_username(self, username):
        self.username = username


class Server:
    def __init__(self):
        self.HOST_ADDR = ""
        self.HOST_PORT = 53000
        self.BUFSIZ = 1024

        self.maxClients = 8
        self.clientCounter = 0
        self.clients = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.HOST_ADDR, self.HOST_PORT))

    # accept clients while their number is smaller than maxClients
    def accept_clients(self):
        try:
            while True:
                if self.clientCounter < 8:
                    client, client_addr = self.socket.accept()
                    self.clients.append(Client(client, client_addr))
                    self.clientCounter += 1

                    c = Client()
                    c.ip = client_addr
                    c.socket = client
                    threading._start_new_thread(self.manage_client, c)
        except:
            pass

    # send an object to a client
    def send_to_client(self, client, obj):
        client.socket.send(bytes(json.dumps(obj) + "\0", "utf-8"))

    # send an object to all clients
    def broadcast(self, obj):
        for c in self.clients:
            self.send_to_client(c, obj)

    # get server ip
    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    # manage a client
    def manage_client(self, client):
        while client.username is None:
            obj = client.recv(self.BUFSIZ).decode()
            if obj["command"] == "username":
                client.username = obj["username"]

        while True:
            print("eskere")

    def start_managing_clients(self):
        for c in self.clients:
            self.manage_client(c)


class ConnectionWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Server")
        self.window.geometry("500x300")
        self.window.config(bg='#4181C0')
        self.window.resizable(False, False)

        self.ipList = tk.Listbox(self.window, bg="#F2F2F2", borderwidth=3, highlightthickness=0, font="30")
        self.ipList.grid(row=1, padx=(100, 100))
        self.ipList.place(x=50, y=50, height=200, width=300)

        self.startButton = tk.Button(self.window, bg="#F2F2F2", text="START", borderwidth=3, highlightthickness=0,
                                     font="30", command=self.start_server)
        self.startButton.place(x=400, y=125, width=60, height=50)

        self.server = Server()
        self.server.socket.listen(10)
        threading._start_new_thread(self.server.accept_clients, ())
        tk.mainloop()

    def start_server(self):
        try:
            self.window.destroy()
            ServerWindow(self.server)
        except:
            self.window.destroy()

    def add_client_to_list(self, client):
        self.server.clients.append(client)
        lbl = self.ipList.cget("text")
        self.ipList.config(text=str(lbl) + str(client.ip) + "\n")
        self.ipList.pack()

class ServerWindow:
    def __init__(self, server):
        self.server = server

        self.window = tk.Tk()
        self.window.title("Client")
        self.window.geometry("500x300")
        self.window.config(bg='#4181C0')
        self.window.resizable(False, False)

        self.server.start_managing_clients()

if __name__ == "__main__":
    c = ConnectionWindow()
