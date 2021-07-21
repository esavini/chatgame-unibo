import json
import random
import socket
import threading
import tkinter as tk
from time import sleep

animals = ["Antilope anonima", "Barbagianni anonimo", "Leone anonimo", "Giraffa anonima", "Scoiattolo anonimo", "Squalo  anonimo", "Orango  anonimo"]

class Player:
    def __init__(self):
        self.username = random.choice(animals)
        self.points = 0



def game_start():

    global accept_answers

    broadcast({
        "cmd": "start"
    })

    broadcast({
        "cmd": "question",
        "question": "di che colore è il cavallo bianco di napoleone?",
        "answers": [
            "bianco",
            "viola",
            "arancione"
        ],
        "time": 10
    })
    accept_answers = True

    sleep(10)

    close_question(0)

    broadcast({
        "cmd": "question",
        "question": "di che colore è il cavallo rosso di napoleone?",
        "answers": [
            "bianco",
            "rosso",
            "arancione"
        ],
        "time": 10
    })

    accept_answers = True

    sleep(10)

    close_question(1)

    winner()


started = False


def start_button():
    '''funzione per avviare il gioco e con esso il tempo'''
    global started
    if not started:
        t = threading.Thread(target=game_start)
        t.start()
        started = True


def get_ip():
    """estrae l'ip per mostrarlo a video """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def receive(client, client_addr):
    """ gestione ricezione dei messaggi."""

    recv_buffer = ""

    while True:
        try:
            data = client.recv(128)
            recv_buffer = recv_buffer + data.decode("utf-8")
            strings = recv_buffer.split('\0')
            for s in strings[:-1]:
                s = json.loads(s)
                command = s["cmd"]
                print(s)
                if command == "join":
                    setUsername(client_addr, s["msg"])
                if command == "sendMsg":
                    send_msg(client_addr, s["msg"])
                if command == "answer":
                    receive_answer(client_addr, s["answer"])

            recv_buffer = strings[-1]

        except OSError:
            break

def receive_answer(client_addr, answer):
    if not accept_answers:
        return

    answers[client_addr] = answer

def close_question(correct_answer):
    global accept_answers
    accept_answers = False

    for client_addr, answer in answers.items():
        if answer == correct_answer:
            players[client_addr].points += 100

    sleep(3)

    broadcast({
        "cmd": "correction",
        "answer": correct_answer
    })

    sleep(3)

    update_leaderboard()


def winner():
    broadcast({
        "cmd": "winner",
        "username": [player.username for player in sorted(list(players.values()), key=lambda a: a.points)][0]
    })

def send_msg(client_addr, msg):
    broadcast({
        "cmd": "receiveMsg",
        "msg": msg,
        "sender": players[client_addr].username
    })

def write_msg(msg):
    object = {
        "command": "",
        "msg": msg
    }
    broadcast(object)


def setUsername(client_addr, username):
    players[client_addr].username = username
    print(username)
    update_leaderboard()


def broadcast(obj):
    """funzione per inviare i messaggi a tutti i client associati alla chat"""
    for c in clients.values():
        send_to_client(c, obj)


def send_to_client(client, obj):
    client.send(bytes(json.dumps(obj) + "\0", "utf-8"))


def accept_clients(server, y):
    '''funzione per la gestione dell'accettazione di client da parte del server
    la chat può accettare al massimo 10 client'''
    if gioco_iniziato.get() == True:
        return

    try:
        while True:
            if client_counter.get() < 10:
                client, client_addr = server.accept()
                indirizzi[client] = client_addr

                threading._start_new_thread(gestisce_client, (client, client_addr))
                client_counter.set(client_counter.get() + 1)

    except:
        pass


def gestisce_client(client, client_addr):
    '''funzione per la gestione dei client'''
    addClientToList(client, client_addr)
    #threading.Thread(target=receive, args=(client, client_addr))
    receive(client, client_addr)
    global game_timer


def addClientToList(client, client_ip):
    clients[client_ip] = client
    players[client_ip] = Player()

    update_leaderboard()

    lbl = label_counter.cget("text")
    label_counter.config(text=str(lbl) + str(client_ip) + "\n")
    label_counter.pack()


def update_leaderboard():
    broadcast({
        "cmd": "leaderboard",
        "leaderboard": [{
            "name": player.username,
            "points": player.points
        } for player in sorted(list(players.values()), key=lambda a: a.points)]
    })


def close_window(window):
    window.destroy()


if __name__ == '__main__':
    # grafica

    window = tk.Tk()
    window.title("Server")
    window.geometry("400x500")
    window.config(bg="#4181C0")
    window.resizable(False, False)

    gioco_iniziato = tk.BooleanVar(False)
    almeno_un_nome = tk.BooleanVar(False)
    client_counter = tk.IntVar(0)

    # start button
    btnStart = tk.Button(window, bg="#4181C0", text="START GAME", font=("Elephant", 30, "bold"),
                         command=lambda: start_button())
    btnStart.place(x=25, y=270, width=350, height=80)

    # list
    label_counter = tk.Label(window, text="", font=("forte", 14, "bold"), bg="#4181C0", relief="sunken")
    label_counter.place(x=20, y=20, width=360, height=200)

    # server ip
    label_ip = tk.Label(window, text="Indirizzo IP:", font=("Perpetua", 25, "bold"), bg="#4181C0",
                        relief="groove")
    label_ip.place(x=50, y=360, width=300, height=50)
    label_ip = tk.Label(window, text=str(get_ip()), font=("Perpetua", 30, "bold"), bg="#4181C0",
                        relief="groove")
    label_ip.place(x=50, y=420, width=300, height=70)

    # variabili nel main
    game_timer = 100

    # gestione della connessione
    server = None
    HOST_ADDR = ""
    HOST_PORT = 53000
    BUFSIZ = 1024
    clients = {}
    players = {}
    indirizzi = {}
    answers = {}
    accept_answers = False

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))

    server.listen(10)
    threading._start_new_thread(accept_clients, (server, " "))
    window.mainloop()
    server.close()


