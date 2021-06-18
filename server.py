# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 21:06:35 2021

@author: Monta
"""

import tkinter as tk
from ttkthemes import ThemedTk
import ttkthemes
import socket
import time
from time import sleep
import threading
import random


def game_start():
    # grafica
    window = tk.Tk()
    window.title("Il Milionario")
    window.geometry("1000x800")
    window.config(bg="slateBlue")
    window.resizable(False, False)

    label_domanda = tk.Label(window, text="Domanda", font=("Perpetua", 35, "bold"), bg="medium slate blue",
                             relief="groove")
    label_domanda.place(x=100, y=250, width=800, height=100)

    btn1 = tk.Button(window, bg="#1e9856", text="RISPOSTA 1", font=("Elephant", 30, "bold"),
                     command=lambda: start_button())
    btn1.place(x=50, y=570, width=400, height=80)

    btn2 = tk.Button(window, bg="#1e9856", text="RISPOSTA 2", font=("Elephant", 30, "bold"),
                     command=lambda: start_button())
    btn2.place(x=550, y=570, width=400, height=80)

    btn3 = tk.Button(window, bg="#1e9856", text="RISPOSTA 3", font=("Elephant", 30, "bold"),
                     command=lambda: start_button())
    btn3.place(x=50, y=680, width=400, height=80)

    btn4 = tk.Button(window, bg="#1e9856", text="RISPOSTA 4", font=("Elephant", 30, "bold"),
                     command=lambda: start_button())
    btn4.place(x=550, y=680, width=400, height=80)


def start_button():
    '''funzione per avviare il gioco e con esso il tempo'''
    broadcast("Game started")
    close_window(window)
    game_start()


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


def broadcast(msg, prefisso=""):
    '''funzione per inviare i messaggi a tutti i client associati alla chat'''
    for utente in clients:
        utente.send(bytes(prefisso, "utf8") + msg)


def accept_clients(server, y):
    '''funzione per la gestione dell'accettazione di client da parte del server
    la chat può accettare al massimo 10 client'''
    if gioco_iniziato.get() == True:
        return

    try:
        while True:
            if client_counter.get() < 10:
                client, client_addr = server.accept()
                client.send(bytes("~ Salve! Digita il tuo Nome seguito dal tasto Invio!", "utf8"))
                indirizzi[client] = client_addr
                threading._start_new_thread(gestisce_client, (client, client_addr))
                client_counter.set(client_counter.get() + 1)
            else:
                client, client_addr = server.accept()
                client.send(bytes("~ Server pieno, ritenta tra un po'", "utf8"))
    except:
        pass


def gestisce_client(client, client_addr):
    '''funzione per la gestione dei client'''
    addClientToList(client_addr)
    global game_timer
    try:
        client.send(bytes("~ Ciao, benvenuto nel gioco di Mirko"))
    except:
        pass


def addClientToList(client_ip):
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
    indirizzi = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))

    server.listen(10)
    threading._start_new_thread(accept_clients, (server, " "))
    window.mainloop()
    server.close()
