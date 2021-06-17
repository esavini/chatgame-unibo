# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 21:06:58 2021

@author: Monta
"""

import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import random
import socket
from socket import AF_INET, socket, SOCK_STREAM


def send(event=None):
    """invio del messaggio sulla soket"""
    try:
        msg = my_msg.get()
        caratteri_vietati = [",", "-", "", "@", "[", "]", "{", "}", "(", ")", "=", "/", "\n", "%", "$", "!", "?", "^",
                             '"', "'", "~", "_"]
        for k in caratteri_vietati:
            msg = msg.replace(k, "")
        my_msg.set("")
        client_socket.send(bytes("plyr" + msg, "utf8"))
    except:
        pass


def receive():
    """ gestione ricezione dei messaggi."""
    global scelte
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg.startswith("~ "):

                if msg.startswith('~ Benvenuto'):
                    io = msg[msg.find("o ") + 2:msg.find('!Se vuoi'):]
                    punteggi = {'- ' + io: 0}
                    aggiorna_punteggi(punteggi)
                if msg.startswith("~ I tuoi compagni di avventura sono "):
                    players = msg[msg.find("avventura sono ") + 15::]
                    if len(players) != 0:
                        for k in players.split(', '):
                            punteggi[k] = 0
                    aggiorna_punteggi(punteggi)
                if msg.endswith(" si è unito all chat!"):
                    punteggi["- " + msg[msg.find("~ ") + 2:msg.find(' si'):]] = 0
                    aggiorna_punteggi(punteggi)
                if msg == "~ ~ MASTER: FINE DEL GIOCO!":

                    esito = "Perso"
                    if max(punteggi.values()) == punteggi["- " + io]:
                        esito = "Vinto"
                    tk.messagebox.showinfo(msg, io + "\nHai " + esito + "\nPunteggio: " + str(punteggi["- " + io]))
                    on_closing()
            elif msg.startswith("_ "):
                scelte = msg[2::].split("@")

            elif '?' in msg:
                a = ""
            elif msg.startswith("- "):
                m = str(msg)
                punteggi[m[:m.find(":"):]] = m[m.find(":") + 2::]
                for k in punteggi.keys():
                    punteggi[k] = int(punteggi[k])
                print(punteggi)
                aggiorna_punteggi(sort_leaderboard(punteggi))
        except OSError:
            break


def aggiorna_punteggi(punteggi):
    """ aggiornamento dei punteggi nella label"""
    p = str(punteggi)


def sort_leaderboard(punteggi):
    """riordina la leaderboard per punteggio decrescente"""
    punteggi_ordinati = {}
    chiavi_ordinate = sorted(punteggi, key=punteggi.get, reverse=True)
    for w in chiavi_ordinate:
        punteggi_ordinati[w] = punteggi[w]
    return punteggi_ordinati


class Timer:
    def __init__(self, min, sec):
        self.minutes = min
        self.seconds = sec
        self.Thread = Thread(target=self.decreaseTime)
        self.termina = False

    def start(self):
        self.Thread.start()

    def stop(self):
        self.termina = True

    def decreaseTime(self):
        while (self.seconds != 0 or self.minutes != 0) and self.termina == False:
            timeLeft.set(self.getTime())
            time.sleep(1)
            if self.seconds > 0:
                self.seconds -= 1
            else:
                self.minutes -= 1
                self.seconds = 59
        return ""


    def getTime(self):
        return '{:02d}:{:02d}'.format(self.minutes, self.seconds)


def game_start():
    #GRAFICA
    finestra.title("Il Milionario")
    finestra.geometry("1300x800")
    finestra.config(bg="#4181C0")

    global timeLeft, t
    timeLeft = tk.StringVar()
    points = 0

    t = Timer(2, 0)
    t.start()
    labelTimer = tk.Label(finestra, textvariable=timeLeft, font=("Perpetua", "40", "bold"), bg="#4181C0")
    labelTimer.place(x=50, y=50, height=50, width=160)

    # label domanda
    label_domanda = tk.Label(finestra, text="in attesa di una domanda...", font=("Perpetua", 35, "bold"),
                             bg="medium slate blue", relief="groove")
    label_domanda.place(x=100, y=250, width=800, height=100)

    # label leaderboard
    lblLeaderboard = tk.Label(finestra, bg="#4181C0", borderwidth=20, text="Leaderboard:\n")
    lblLeaderboard.place(x=1000, y=10, height=290, width=300)

    # listbox messaggi
    messageList = tk.Listbox(finestra, bg="#F2F2F2", borderwidth=0, font="30")
    messageList.place(x=1000, y=300, height=440, width=300)

    # textbox sendMessage
    msgTextBox = tk.Entry(finestra, borderwidth=0, font="30")
    msgTextBox.place(x=1000, y=740, height=50, width=250)

    # button sendMessage
    sendMsgButton = tk.Button(finestra, text="SEND", borderwidth=0, font="'bold'")
    sendMsgButton.place(x=1250, y=740, height=50, width=50)

    global btn1, btn2, btn3, btn4
    btn1 = tk.Button(finestra, bg="#1e9856", text="RISPOSTA 1", font=("Elephant", 30, "bold"))
    btn1.place(x=50, y=570, width=400, height=80)

    btn2 = tk.Button(finestra, bg="#1e9856", text="RISPOSTA 2", font=("Elephant", 30, "bold"))
    btn2.place(x=550, y=570, width=400, height=80)

    btn3 = tk.Button(finestra, bg="#1e9856", text="RISPOSTA 3", font=("Elephant", 30, "bold"))
    btn3.place(x=50, y=680, width=400, height=80)

    btn4 = tk.Button(finestra, bg="#1e9856", text="RISPOSTA 4", font=("Elephant", 30, "bold"))
    btn4.place(x=550, y=680, width=400, height=80)
    disableButtons()


def disableButtons():
    btn1['state'] = tk.DISABLED
    btn2['state'] = tk.DISABLED
    btn3['state'] = tk.DISABLED
    btn4['state'] = tk.DISABLED


def enableButtons():
    btn1['state'] = tk.NORMAL
    btn2['state'] = tk.NORMAL
    btn3['state'] = tk.NORMAL
    btn4['state'] = tk.NORMAL


def risposta(var):
    """invio della risposta al server"""
    msg = "answ" + var
    client_socket.send(bytes(msg, "utf8"))


def chiusura():
    """apparizione messagebox e gestione della chiusura"""
    tk.messagebox.showinfo("peccato!", scelte[3])
    on_closing()


def on_closing(event=None):
    """chiusura della connessione con il singolo client e distruzione della finestra"""
    try:
        client_socket.send(bytes("quit", "utf8"))
        client_socket.close()
        finestra.destroy()
        t.stop()
    except:
        finestra.destroy()


def question(event=None):
    """richiesta della domanda al server"""
    msg = "qstn"
    client_socket.send(bytes(msg, "utf8"))


def avvio():
    '''funzione che si occupa di gestire la grafica dell'interfaccia d'avvio e
        della gestione della connessione con il server'''
    try:
        print(entry_host.get())
        HOST = str(entry_host.get())
        PORT = 53000
        ADDR = (HOST, PORT)
        client_socket.connect(ADDR)

        entry_host.destroy()
        button_host.destroy()
        istruzioni.destroy()
        titolo.destroy()
        receive_thread = Thread(target=receive)
        receive_thread.start()
    except:
        pass


def ipCheck():
    try:
        IP = str(entry_host.get())
        PORT = 53000
        ADDR = (IP, PORT)
        client_socket.connect(ADDR)
        return True
    except:
        return False


def destroyMenu():
    if ipCheck():
        titolo.destroy()
        istruzioni.destroy()
        entry_host.destroy()
        button_host.destroy()

        game_start()
    else:
        istruzioni.config(text="IP NON VALIDO, RIPROVA")


def gotoIpMenu():
    if 0 < len(entry_host.get()) < 8:
        istruzioni.config(text="INSERISCI IP SERVER")
        entry_host.delete(0, tk.END)
        button_host.config(text="START", command=destroyMenu)
    else:
        istruzioni.config(text="USERNAME NON VALIDO, RIPROVA")


if __name__ == '__main__':
    # grafica
    finestra = tk.Tk()
    finestra.title("Client")
    finestra.geometry("500x300")
    finestra.config(bg='#4181C0')
    finestra.resizable(False, False)

    # title
    titolo = tk.Label(finestra, text="CHATGAME", bg="#7AB6FF", relief="groove", font=("chiller", 50))
    titolo.place(x=0, y=0, width=500)

    # name textbox
    entry_host = tk.Entry(finestra, bg="#F2F2F2", font="30")
    entry_host.place(x=50, y=200, width=340, height=40)

    # description
    istruzioni = tk.Label(finestra, text="INSERISCI IL TUO USERNAME", font=("courier"), relief="sunken")
    istruzioni.place(x=50, y=140, width=400)

    # avvio button
    button_host = tk.Button(finestra, text="SELECT", bg="#7AB6FF", font=("courier"), command=gotoIpMenu)
    button_host.place(x=390, y=200, width=60, height=40)

    finestra.protocol("WM_DELETE_WINDOW", on_closing)

    BUFSIZ = 1024
    client_socket = socket(AF_INET, SOCK_STREAM)

    # avvia l'esecuzione della Finestra
    tk.mainloop()
