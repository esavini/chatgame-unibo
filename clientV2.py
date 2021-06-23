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
import json
from socket import AF_INET, socket, SOCK_STREAM

punteggio = {
    "cmd": "leaderboard",
    "leaderboard": [{
            "name": "ruspa",
            "points": 5
        }, {
            "name": "eskere",
            "points": 54
        }],
    "you": 500
}
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

BUFFERSIZE = 4096

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


class GameWindow:
    def __init__(self, username, clientSocket, bufferSize):
        self.player = Player(username)
        self.clientSocket = clientSocket
        self.bufferSize = bufferSize

        self.finestra = tk.Tk()
        self.finestra.title("CHATGAME")
        self.finestra.geometry("1300x800")
        self.finestra.config(bg="#4181C0")

        self.timer = 0
        self.timeLeft = tk.StringVar()

        # label timer
        self.labelTimer = tk.Label(self.finestra, textvariable=self.timeLeft, font=("Perpetua", "40", "bold"), bg="#4181C0",
                                   borderwidth=2, relief="solid")
        self.labelTimer.place(x=50, y=50, height=50, width=160)

        # label question
        self.labelQuestion = tk.Label(self.finestra, text="in attesa di una domanda...", font=("Perpetua", 30, "bold"),
                                      bg="medium slate blue", relief="groove")
        self.labelQuestion.place(x=100, y=250, width=800, height=100)

        # label leaderboard
        self.labelLeaderboard = tk.Label(self.finestra, bg="#4181C0", borderwidth=20, text="Leaderboard:",
                                         font=("Perpetua", 18, "bold"))
        self.labelLeaderboard.place(x=1000, y=20, height=50, width=300)

        # listbox message
        self.messageList = tk.Listbox(self.finestra, bg="#F2F2F2", borderwidth=0, highlightthickness=0, font="30")
        self.messageList.grid(row=1, padx=(100, 100))
        self.messageList.place(x=1000, y=300, height=440, width=300)

        # textbox sendMessage
        self.msgTextBox = tk.Entry(self.finestra, borderwidth=0, font="30")
        self.msgTextBox.place(x=1000, y=740, height=50, width=250)

        # leaderboard
        self.lstLeaderboard = tk.Listbox(self.finestra, bg="#4181C0", font=("Perpetua", 15, "bold"))
        self.lstLeaderboard.place(x=1000, y=70, width=300, height=230)
        self.updatePoints(punteggio)

        # button sendMessage
        self.sendMsgButton = tk.Button(self.finestra, text="SEND", borderwidth=0, font="'bold'",
                                       command=lambda: self.addChatMessage(self.msgTextBox.get()))
        self.sendMsgButton.place(x=1250, y=740, height=50, width=50)

        # answer buttons
        self.btn1 = tk.Button(self.finestra, bg="#1e9856", text="RISPOSTA 1", font=("Elephant", 30, "bold"))
        self.btn1.place(x=50, y=570, width=400, height=80)

        self.btn2 = tk.Button(self.finestra, bg="#1e9856", text="RISPOSTA 2", font=("Elephant", 30, "bold"))
        self.btn2.place(x=550, y=570, width=400, height=80)

        self.btn3 = tk.Button(self.finestra, bg="#1e9856", text="RISPOSTA 3", font=("Elephant", 30, "bold"))
        self.btn3.place(x=300, y=680, width=400, height=80)
        self.disableButtons()

    def disableButtons(self):
        self.btn1['state'] = tk.DISABLED
        self.btn2['state'] = tk.DISABLED
        self.btn3['state'] = tk.DISABLED

    def enableButtons(self):
        self.btn1['state'] = tk.NORMAL
        self.btn2['state'] = tk.NORMAL
        self.btn3['state'] = tk.NORMAL

    def setTimeLeft(self, time):
        self.timeLeft = time

    def getTimeLeft(self):
        return self.timeLeft

    def setQuestion(self, question):
        self.enableButtons()
        self.labelQuestion.config(text=question["question"])

        self.btn1.config(text=question["answers"][0])
        self.btn2.config(text=question["answers"][1])
        self.btn3.config(text=question["answers"][2])

        seconds = int(question["time"])
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        self.timer = Timer(minutes, seconds)
        self.timer.start()

    def updatePoints(self, punteggi):
        self.lstLeaderboard.delete(first=0, last=tk.END)
        counter = 1

        if punteggi["you"] > self.player.points:
            self.player.points = punteggi["you"]
            self.addChatMessage("correct answer")
        else:
            self.addChatMessage("wrong answer")

        for player in punteggi["leaderboard"]:
            name = player["name"]
            point = player["points"]

            self.lstLeaderboard.insert(counter, name + " : " + str(point))
            counter += 1

    def addChatMessage(self, msg):
        if msg == "":
            return

        self.messageList.insert(self.messageList.size() + 1, "ME: " + msg)
        self.finestra.update_idletasks()
        self.msgTextBox.delete(0, tk.END)
        self.sendMessageToServer(msg)

    def addExternalChatMessage(self, messageObject):
        self.messageList.insert(self.messageList.size() + 1, messageObject["sender"] + ": " + messageObject["msg"])
        self.finestra.update_idletasks()

    def sendUsernameToServer(self, nickname):
        msg = {
            "cmd": "join",
            "msg": nickname
        }
        self.clientSocket.send(bytes(msg), "utf8")

    def sendMessageToServer(self, msg):
        msg = {
            "cmd": "sendMsg",
            "msg": msg
        }
        data = json.dumps(msg)
        self.clientSocket.send(bytes(data, encoding="utf-8"))

    def sendAnswerToServer(self, idAnswer):
        msg = {
            "cmd": "answer",
            "answer": idAnswer
        }
        data = json.dumps(msg)
        self.clientSocket.send(bytes(data, encoding="utf-8"))

    def receive(self):
        """ gestione ricezione dei messaggi."""
        while True:
            try:
                msg = json.loads(self.clientSocket.recv(self.bufferSize).decode("utf8"))
                command = msg["cmd"]

                if command == "question":
                    setQuestion(msg)
                if command == "receiveMsg":
                    addExternalChatMessage(msg)
                if command == "leaderboard":
                    updatePoints(msg)

            except OSError:
                break


class ConnectionWindow:
    def __init__(self):
        self.finestra = tk.Tk()
        self.finestra.title("Client")
        self.finestra.geometry("500x300")
        self.finestra.config(bg='#4181C0')
        self.finestra.resizable(False, False)

        # title
        self.title = tk.Label(self.finestra, text="CHATGAME", bg="#7AB6FF", relief="groove", font=("chiller", 50))
        self.title.place(x=0, y=0, width=500)

        # name textbox
        self.txtName = tk.Entry(self.finestra, bg="#F2F2F2", font="30")
        self.txtName.place(x=50, y=200, width=340, height=40)

        # description
        self.instruction = tk.Label(self.finestra, text="INSERISCI IL TUO USERNAME", font=("courier"), relief="sunken")
        self.instruction.place(x=50, y=140, width=400)

        # avvio button
        self.btnNext = tk.Button(self.finestra, text="SELECT", bg="#7AB6FF", font=("courier"), command=self.ipMenu)
        self.btnNext.place(x=390, y=200, width=60, height=40)

        self.finestra.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bufferSize = BUFFERSIZE
        self.clientSocket = socket(AF_INET, SOCK_STREAM)

        tk.mainloop()

    def ipMenu(self):
        if 0 < len(self.txtName.get()) < 8:
            self.username = self.txtName.get()

            self.instruction.config(text="INSERISCI IP SERVER")
            self.txtName.delete(0, tk.END)
            self.btnNext.config(text="START", command=self.destroyMenu)
        else:
            self.instruction.config(text="USERNAME NON VALIDO, RIPROVA")

    def ipCheck(self):
        try:
            IP = str(self.txtName.get())
            PORT = 53000
            ADDR = (IP, PORT)
            self.clientSocket.connect(ADDR)
            return True
        except:
            return False

    def destroyMenu(self):
        if self.ipCheck():
            self.finestra.destroy()
            startGame(self.username, self.clientSocket, self.bufferSize)
        else:
            self.istruzioni.config(text="IP NON VALIDO, RIPROVA")

    def on_closing(self):
        try:
            self.clientSocket.send(bytes("quit", "utf8"))
            self.clientSocket.close()
            self.finestra.destroy()
        except:
            self.finestra.destroy()


class Player:
    def __init__(self, name):
        self.username = name
        self.points = 0
        self.rightAnswer = 0


def startGame(username, client, bufferSize):
    GameWindow(username, client, bufferSize)

if __name__ == "__main__":
    c = ConnectionWindow()