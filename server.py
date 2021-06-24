# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 21:06:35 2021

@author: Monta
"""
import json
import socket
import threading
import tkinter as tk
from time import sleep


def game_start():
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

    sleep(13)

    broadcast({
        "cmd": "correction",
        "answer": 0
    })

    sleep(3)

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

    sleep(13)

    broadcast({
        "cmd": "correction",
        "answer": 1
    })

    sleep(3)




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
    global game_timer



def addClientToList(client, client_ip):
    clients[client_ip] = client
    lbl = label_counter.cget("text")
    label_counter.config(text=str(lbl) + str(client_ip) + "\n")
    label_counter.pack()


def close_window(window):
    window.destroy()


if __name__ == '__main__':
    # grafica

    window = tk.Tk()
    window.title("Server")
    window.geometry("400x500")
    window.config(bg="slateBlue")
    window.resizable(False, False)

    gioco_iniziato = tk.BooleanVar(False)
    almeno_un_nome = tk.BooleanVar(False)
    client_counter = tk.IntVar(0)

    # start button
    btnStart = tk.Button(window, bg="#1e9856", text="START GAME", font=("Elephant", 30, "bold"),
                         command=lambda: start_button())
    btnStart.place(x=25, y=270, width=350, height=80)

    # list
    label_counter = tk.Label(window, text="", font=("forte", 14, "bold"), bg="medium slate blue", relief="sunken")
    label_counter.place(x=20, y=20, width=360, height=200)

    # server ip
    label_ip = tk.Label(window, text="Indirizzo IP:", font=("Perpetua", 25, "bold"), bg="medium slate blue",
                        relief="groove")
    label_ip.place(x=50, y=360, width=300, height=50)
    label_ip = tk.Label(window, text=str(get_ip()), font=("Perpetua", 30, "bold"), bg="medium slate blue",
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
    usernames = {}
    indirizzi = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))

    server.listen(10)
    threading._start_new_thread(accept_clients, (server, " "))
    window.mainloop()
    server.close()
