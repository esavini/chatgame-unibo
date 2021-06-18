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

def sendUsernameToServer(nickname):
    msg = {
        "cmd": "join",
        "msg": nickname
    }
    client_socket.send(bytes(msg), "utf8")

def sendMessageToServer(msg):
    msg = {
        "cmd": "sendMsg",
        "msg": msg
    }
    client_socket.send(bytes(msg), "utf8")

def sendAnswerToServer(idAnswer):
    msg = {
        "cmd": "answer",
        "answer": idAnswer
    }
    client_socket.send(bytes(msg), "utf8")

def receive():
    """ gestione ricezione dei messaggi."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            command = msg["cmd"]

            if command == "question":
                setQuestion(msg)
            if command == "receiveMsg":
                addExternalChatMessage(msg)
            if command == "leaderboard":
                updatePoints(msg)

        except OSError:
            break


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
        timeLeft.set(self.getTime())
        self.termina = True
        return ""


    def getTime(self):
        return '{:02d}:{:02d}'.format(self.minutes, self.seconds)


class Player:
    def __init__(self, name):
        self.username = name
        self.points = 0
        self.rightAnswer = 0

def updatePoints(punteggi):
    lstLeaderboard.delete(first=0, last=tk.END)
    counter = 1

    if punteggi["you"] > p.points:
        p.points = punteggi["you"]
        addChatMessage("correct answer")
    else:
        addChatMessage("wrong answer")

    for player in punteggi:
        name = player["name"]
        point = player["points"]

        lstLeaderboard.insert(counter, name + " : " + str(point))
        counter += 1

def addChatMessage(msg):
    if msg == "":
        return

    messageList.insert(messageList.size()+1, "ME: " + msg)
    finestra.update_idletasks()
    msgTextBox.delete(0, tk.END)
    sendMessageToServer(msg)

def addExternalChatMessage(messageObject):
    messageList.insert(messageList.size()+1, messaggio["sender"] + ": " + messaggio["msg"])
    finestra.update_idletasks()
    msgTextBox.delete(0, tk.END)

global t
def setQuestion(question):
    label_domanda.config(text=question["question"])

    btn1.config(text=question["answers"][0])
    btn2.config(text=question["answers"][1])
    btn3.config(text=question["answers"][2])

    seconds = int(question["time"])
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)
    t = Timer(minutes, seconds)
    t.start()





punteggio = [
    {
        "name": "ruspa",
        "points": 5
    },
{
        "name": "eskere",
        "points": 54
    }
]
domanda = {
    "cmd": "question",
    "question": "di che colore è il cavallo bianco di napoleone?",
    "answers": [
        "rosso",
        "viola",
        "arancione",
        "verde"
    ],
    "time": 10
}
messaggio = {
    "cmd": "receiveMsg",
    "msg": "TVOIIAAA",
    "sender": "Azel con la mamma troia"
}

def game_start():
    #GRAFICA
    finestra.title("CHATGAME")
    finestra.geometry("1300x800")
    finestra.config(bg="#4181C0")

    global timeLeft
    timeLeft = tk.StringVar()
    point = 0

    labelTimer = tk.Label(finestra, textvariable=timeLeft, font=("Perpetua", "40", "bold"), bg="#4181C0", borderwidth=2, relief="solid")
    labelTimer.place(x=50, y=50, height=50, width=160)

    # label domanda
    global label_domanda
    label_domanda = tk.Label(finestra, text="in attesa di una domanda...", font=("Perpetua", 30, "bold"), bg="medium slate blue", relief="groove")
    label_domanda.place(x=100, y=250, width=800, height=100)

    # label leaderboard
    lblLeaderboard = tk.Label(finestra, bg="#4181C0", borderwidth=20, text="Leaderboard:", font=("Perpetua", 18, "bold"))
    lblLeaderboard.place(x=1000, y=20, height=50, width=300)

    #leaderboard
    global lstLeaderboard
    lstLeaderboard = tk.Listbox(finestra, bg="#4181C0", font=("Perpetua", 15, "bold"))
    lstLeaderboard.place(x=1000, y=70, width=300, height=230)
    updatePoints(punteggio)

    # listbox messaggi
    global messageList
    messageList = tk.Listbox(finestra, bg="#F2F2F2", borderwidth=0, highlightthickness=0, font="30")
    messageList.grid(row=1, padx=(100, 100))
    messageList.place(x=1000, y=300, height=440, width=300)

    # textbox sendMessage
    global msgTextBox
    msgTextBox = tk.Entry(finestra, borderwidth=0, font="30")
    msgTextBox.place(x=1000, y=740, height=50, width=250)

    # button sendMessage
    messageCounter = 0
    sendMsgButton = tk.Button(finestra, text="SEND", borderwidth=0, font="'bold'", command=lambda: addChatMessage(msgTextBox.get()))
    sendMsgButton.place(x=1250, y=740, height=50, width=50)

    global btn1, btn2, btn3
    btn1 = tk.Button(finestra, bg="#1e9856", text="RISPOSTA 1", font=("Elephant", 30, "bold"))
    btn1.place(x=50, y=570, width=400, height=80)

    btn2 = tk.Button(finestra, bg="#1e9856", text="RISPOSTA 2", font=("Elephant", 30, "bold"))
    btn2.place(x=550, y=570, width=400, height=80)

    btn3 = tk.Button(finestra, bg="#1e9856", text="RISPOSTA 3", font=("Elephant", 30, "bold"))
    btn3.place(x=300, y=680, width=400, height=80)

    disableButtons()
    setQuestion(domanda)
    addExternalChatMessage(messaggio)

def disableButtons():
    btn1['state'] = tk.DISABLED
    btn2['state'] = tk.DISABLED
    btn3['state'] = tk.DISABLED
def enableButtons():
    btn1['state'] = tk.NORMAL
    btn2['state'] = tk.NORMAL
    btn3['state'] = tk.NORMAL


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
    except:
        finestra.destroy()

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
        global p
        p = Player(entry_host.get())
        sendUsernameToServer(p.username)
        
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
