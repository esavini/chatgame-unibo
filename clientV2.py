# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 21:06:58 2021

@author: Monta
"""

import json
import socket
import struct
import time
import tkinter as tk
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

BUFFERSIZE = 4096
listMessagesInQueue = []
leaderboard = []
lastQuestion = None
correction = None


class Timer:
    def __init__(self, min, sec):
        self.minutes = min
        self.seconds = sec
        self.Thread = Thread(target=self.decreaseTime)
        self.time = ""
        self.termina = False

    def start(self):
        self.Thread.start()

    def stop(self):
        self.termina = True

    def decreaseTime(self):
        while (self.seconds != 0 or self.minutes != 0) and self.termina == False:
            self.time = self.getTime()
            time.sleep(1)
            if self.seconds > 0:
                self.seconds -= 1
            else:
                self.minutes -= 1
                self.seconds = 59
        self.time = self.getTime()
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
        self.labelTimer = tk.Label(self.finestra, textvariable=self.timeLeft, font=("Perpetua", "40", "bold"),
                                   bg="#4181C0",
                                   borderwidth=2, relief="solid")
        self.labelTimer.place(x=50, y=50, height=50, width=160)

        # label question
        self.labelQuestion = tk.Label(self.finestra, text="...in attesa di una domanda...",
                                      font=("Perpetua", 30, "bold"),
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

        # button sendMessage
        self.sendMsgButton = tk.Button(self.finestra, text="SEND", borderwidth=0, font="'bold'",
                                       command=lambda: self.sendMessageToServer(self.msgTextBox.get()))
        self.sendMsgButton.place(x=1250, y=740, height=50, width=50)

        global correction
        # answer buttons
        self.btn1 = tk.Button(self.finestra, bg="white", text="RISPOSTA 1", font=("Elephant", 30, "bold"),
                              command=lambda: self.sendAnswerToServer(0))
        self.btn1.place(x=50, y=570, width=400, height=80)

        self.btn2 = tk.Button(self.finestra, bg="white", text="RISPOSTA 2", font=("Elephant", 30, "bold"),
                              command=lambda: self.sendAnswerToServer(1))
        self.btn2.place(x=550, y=570, width=400, height=80)

        self.btn3 = tk.Button(self.finestra, bg="white", text="RISPOSTA 3", font=("Elephant", 30, "bold"),
                              command=lambda: self.sendAnswerToServer(2))
        self.btn3.place(x=300, y=680, width=400, height=80)

        self.disableButtons()

        t = Thread(target=self.receive)
        t.start()
        self.updateMessageList()
        self.update_leaderboard()
        self.updateQuestion()
        self.refreshButtons()

    def disableButtons(self):
        self.btn1['state'] = tk.DISABLED
        self.btn2['state'] = tk.DISABLED
        self.btn3['state'] = tk.DISABLED

    def enableButtons(self):
        self.btn1['state'] = tk.NORMAL
        self.btn2['state'] = tk.NORMAL
        self.btn3['state'] = tk.NORMAL

    def setQuestion(self, question):
        global lastQuestion
        lastQuestion = question

    def updateCorrection(self, corr):
        global correction
        print(corr)
        correction = corr["answer"]

    def refreshButtons(self):
        global correction
        print(correction)
        self.btn1.config(bg=("green" if correction == 0 else "white"))
        self.btn2.config(bg=("green" if correction == 1 else "white"))
        self.btn3.config(bg=("green" if correction == 2 else "white"))

        self.finestra.after(250, self.refreshButtons)

    def updateQuestion(self):
        global lastQuestion
        global correction

        if lastQuestion is not None:
            self.enableButtons()

            self.labelQuestion.config(text=lastQuestion["question"])
            self.btn1.config(bg="white", text=lastQuestion["answers"][0])
            self.btn2.config(bg="white", text=lastQuestion["answers"][1])
            self.btn3.config(bg="white", text=lastQuestion["answers"][2])

            seconds = int(lastQuestion["time"])
            minutes = int(seconds / 60)
            seconds = int(seconds % 60)
            self.timer = Timer(minutes, seconds)
            self.timer.start()
            self.updateTime()
            lastQuestion = None
            correction = None

        self.finestra.after(250, self.updateQuestion)

    def updateTime(self):
        self.timeLeft.set(self.timer.time)
        if not self.timer.time == "00:00":
            self.finestra.after(250, self.updateTime)

    def updateMessageList(self):
        global listMessagesInQueue
        if len(listMessagesInQueue) > 0:
            for message in listMessagesInQueue:
                self.messageList.insert("end", message)
            listMessagesInQueue = []
            self.messageList.update()
        self.finestra.after(500, self.updateMessageList)

    def update_leaderboard(self):
        global leaderboard

        self.lstLeaderboard.delete(0, tk.END)

        for player in leaderboard:
            self.lstLeaderboard.insert("end", player)

        self.lstLeaderboard.update()
        self.finestra.after(500, self.update_leaderboard)

    def updatePoints(self, punteggi):
        global leaderboard
        leaderboard.clear()

        for p in punteggi["leaderboard"]:
            leaderboard.insert(len(leaderboard), p["name"] + ": " + str(p["points"]))

    def addChatMessage(self, string):
        self.messageList.insert("end", string)

    def addExternalChatMessage(self, messageObject):
        msg = messageObject["sender"] + ": " + messageObject["msg"]
        global listMessagesInQueue
        listMessagesInQueue.insert(len(listMessagesInQueue), msg)

    def sendUsernameToServer(self, nickname):
        object = {
            "cmd": "join",
            "msg": nickname
        }
        data = json.dumps(object)
        self.clientSocket.send(bytes(data, encoding="utf-8"))

    def sendMessageToServer(self, msg):
        object = {
            "cmd": "sendMsg",
            "msg": msg
        }
        data = json.dumps(object)
        self.clientSocket.send(bytes(data, encoding="utf-8"))

    def sendAnswerToServer(self, btnNumber):
        self.disableButtons()
        object = {
            "cmd": "answer",
            "answer": btnNumber
        }
        data = json.dumps(object)
        self.clientSocket.send(bytes(data, encoding="utf-8"))



    def receive(self):
        """ gestione ricezione dei messaggi."""

        recv_buffer = ""

        while True:
            try:
                data = self.clientSocket.recv(128)
                recv_buffer = recv_buffer + data.decode("utf-8")
                strings = recv_buffer.split('\0')
                for s in strings[:-1]:
                    s = json.loads(s)
                    command = s["cmd"]

                    if command == "question":
                        self.setQuestion(s)
                    if command == "receiveMsg":
                        self.addExternalChatMessage(s)
                    if command == "leaderboard":
                        self.updatePoints(s)
                    if command == "winner":
                        self.on_closing()
                        WinnerWindow(s)
                    if command == "correction":
                        self.updateCorrection(s)

                recv_buffer = strings[-1]

            except OSError:
                break

    def on_closing(self):
        try:
            self.clientSocket.close()
            self.finestra.destroy()
        except:
            self.finestra.destroy()


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
            self.clientSocket.close()
            self.finestra.destroy()
        except:
            self.finestra.destroy()


class WinnerWindow:
    def __init__(self, msg):
        self.finestra = tk.Tk()
        self.finestra.title("chatgame")
        self.finestra.geometry("700x200")
        self.finestra.config(bg='#4181C0')
        self.finestra.resizable(False, False)

        # label
        self.label = tk.Label(self.finestra, relief="solid", borderwidth=1, fg="black", font=("Perpetua", "25", "bold"))
        self.label.place(x=50, y=75, height=50, width=500)
        self.label.config(text="Winner: " + msg["username"])

        # close button
        self.closeBtn = tk.Button(self.finestra, text="CLOSE", bg="#7AB6FF", font=("Perpetua", "13", "bold"),
                                  command=self.close)
        self.closeBtn.place(x=550, y=75, width=70, height=50)

        self.finestra.protocol("WM_DELETE_WINDOW", self.close)
        self.bufferSize = BUFFERSIZE
        self.clientSocket = socket(AF_INET, SOCK_STREAM)

        tk.mainloop()

    def close(self):
        try:
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


msg = {
    "cmd": "winner",
    "username": "gesu cristo"
}

if __name__ == "__main__":
    c = ConnectionWindow()
