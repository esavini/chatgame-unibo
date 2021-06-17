# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 21:06:58 2021

@author: Monta
"""

import tkinter as tk
from tkinter import messagebox
from threading import Thread
import socket
from socket import AF_INET, socket, SOCK_STREAM
import random

def send(event=None):
    """invio del messaggio sulla soket"""
    try:
        msg = my_msg.get()
        caratteri_vietati=[",","-","","@","[","]","{","}","(",")","=","/","\n","%","$","!","?","^",'"',"'","~","_"]
        for k in caratteri_vietati:
            msg=msg.replace(k,"")
        my_msg.set("")
        client_socket.send(bytes("plyr"+msg, "utf8"))
    except:
        pass
    
def receive():
    """ gestione ricezione dei messaggi."""
    global scelte
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg.startswith("~ "):
                msg_list.insert(tk.END, msg.replace("~ ~ ","").replace("~ ",""))
                if msg.startswith('~ Benvenuto'):
                    io=msg[msg.find("o ")+2:msg.find('!Se vuoi'):]
                    punteggi={'- '+io:0}
                    aggiorna_punteggi(punteggi)
                if msg.startswith("~ I tuoi compagni di avventura sono "):
                    players=msg[msg.find("avventura sono ")+15::]
                    if len(players) !=0:
                        for k in players.split(', '):
                            punteggi[k]=0
                    aggiorna_punteggi(punteggi)
                if msg.endswith(" si è unito all chat!"):
                    punteggi["- "+msg[msg.find("~ ")+2:msg.find(' si'):]]=0
                    aggiorna_punteggi(punteggi)
                if msg == "~ ~ MASTER: FINE DEL GIOCO!":
                    disable_all()
                    esito="Perso"
                    if max(punteggi.values())==punteggi["- "+io]:
                        esito="Vinto"
                    tk.messagebox.showinfo(msg,io+"\nHai "+esito+"\nPunteggio: "+str(punteggi["- "+io]))
                    on_closing()
            elif msg.startswith("_ "):
                scelte=msg[2::].split("@")
                enable_buttons()
            elif '?' in msg:
                risposte(msg)
            elif msg.startswith("- "):
                m=str(msg)
                punteggi[m[:m.find(":"):]]=m[m.find(":")+2::]
                for k in punteggi.keys():
                    punteggi[k]=int(punteggi[k])
                print(punteggi)
                aggiorna_punteggi(sort_leaderboard(punteggi))
        except OSError:  
            break

def aggiorna_punteggi(punteggi):
    """ aggiornamento dei punteggi nella label"""
    p=str(punteggi)
    Classifica_Giocatori.config(text=p.replace('{','').replace('}','').replace(', ','\n').replace("'",''))

def sort_leaderboard(punteggi):
    """riordina la leaderboard per punteggio decrescente"""
    punteggi_ordinati = {}
    chiavi_ordinate = sorted(punteggi, key=punteggi.get, reverse=True)
    for w in chiavi_ordinate:
        punteggi_ordinati[w] = punteggi[w]
    return punteggi_ordinati

def risposte(q):
    """posiziona i bottoni e le label delle domande"""
    disable_buttons()
    label_question.config(text=q[:q.find('?')+1:], relief="sunken")
    label_question.place(x=10,y=400,height=30,width=680)
    a_button.config(text=q[q.find('A=')+2:q.find('\t'):])
    a_button.place(x=50,y=450, width=100, height=30)
    b_button.config(text=q[q.find('B=')+2::])
    b_button.place(x=550,y=450, width=100, height=30)


def game_start():
    #grafica
    window=tk.Tk()
    window.title("Il Milionario")
    window.geometry("1000x800")
    window.config(bg="slateBlue")
    window.resizable(False,False)
    
    label_domanda = tk.Label(window, text="Domanda", font=("Perpetua",35,"bold"), bg="medium slate blue", relief="groove")
    label_domanda.place(x=100, y=250, width=800, height=100)
    
    
    btn1 = tk.Button(window, bg="#1e9856", text="RISPOSTA 1", font=("Elephant",30,"bold"))
    btn1.place(x=50, y=570, width=400, height=80)
    
    btn2 = tk.Button(window, bg="#1e9856", text="RISPOSTA 2", font=("Elephant",30,"bold"))
    btn2.place(x=550, y=570, width=400, height=80)
    
    btn3 = tk.Button(window, bg="#1e9856", text="RISPOSTA 3", font=("Elephant",30,"bold"))
    btn3.place(x=50, y=680, width=400, height=80)
    
    btn4 = tk.Button(window, bg="#1e9856", text="RISPOSTA 4", font=("Elephant",30,"bold"))
    btn4.place(x=550, y=680, width=400, height=80)
    

def disable_all():
    """disabilita tutti bottoni"""
    disable_buttons()
    disable_risp()
    
def disable_risp():
    """elimina i bottoni delle risposte"""
    label_question.place_forget()
    a_button.place_forget()
    b_button.place_forget()
    
def disable_buttons():
    """disabilita i tre bottoni question1/question2/trabocchetto"""
    q1_button['state']=tk.DISABLED
    q2_button['state']=tk.DISABLED
    t_button['state']=tk.DISABLED

def enable_buttons():
    """abilita i tre bottoni question1/question2/trabocchetto."""
    q1_button['state']=tk.NORMAL
    q2_button['state']=tk.NORMAL
    t_button['state']=tk.NORMAL
    shuffle_buttons()

def shuffle_buttons():
    """riordina randomicamente i bottoni question1/question2/trabocchetto"""
    global scelte
    random.shuffle(comandi)
    q1_button.config(text=scelte[0], command=comandi[0])
    q2_button.config(text=scelte[1], command=comandi[1])
    t_button.config(text=scelte[2], command=comandi[2])


def risposta(var):
    """invio della risposta al server"""
    msg="answ"+var
    disable_risp()    
    client_socket.send(bytes(msg, "utf8"))

def chiusura():
    """apparizione messagebox e gestione della chiusura"""
    tk.messagebox.showinfo("peccato!",scelte[3])
    on_closing()

def on_closing(event=None):
    """chiusura della connessione con il singolo client e distruzione della finestra"""
    try:
        client_socket.send(bytes("quit","utf8"))
        client_socket.close()
        finestra.destroy()
    except:
        finestra.destroy()
        
def question(event=None):
    """richiesta della domanda al server"""
    msg="qstn"
    client_socket.send(bytes(msg, "utf8"))
        
def avvio():
    '''funzione che si occupa di gestire la grafica dell'interfaccia d'avvio e
        della gestione della connessione con il server''' 
    try:
        print(entry_host.get())
        HOST=str(entry_host.get())
        PORT=53000
        ADDR=(HOST,PORT)
        client_socket.connect(ADDR)

        msg_list.place(x=10,y=10,height=300,width=300)
        scrollbarx.place(x=10,y=310,height=20,width=300)
        scrollbary.place(x=310,y=10,height=320,width=20)
        txt.place(x=340,y=10,height=20,width=170)
        entry_field.place(x=340,y=310,width=350)
        q1_button.place(x=10,y=350,width=150)
        q2_button.place(x=170,y=350,width=150)
        t_button.place(x=330,y=350,width=150)
        send_button.place(x=590,y=350,width=100)
        Classifica_Giocatori.place(x=340,y=40,width=350)
        entry_host.destroy()
        button_host.destroy()
        istruzioni.destroy()
        titolo.destroy()
        receive_thread = Thread(target=receive)
        receive_thread.start()
    except:
        pass
    
if __name__ == '__main__':
    # grafica
    finestra = tk.Tk()
    finestra.title("Client")
    finestra.geometry("700x500")
    finestra.config(bg="dark orange")
    finestra.resizable(False,False)

    my_msg = tk.StringVar()
    indice_giocatore= tk.IntVar(0)
    scelte=["","","",""]

    #title
    titolo=tk.Label(finestra,text="CHATGAME", bg="#7AB6FF", relief="groove", font=("chiller",50))
    titolo.place(x=0,y=0,width=700)

    #description
    istruzioni=tk.Label(finestra,text="INSERISCI L'INDIRIZZO IP DEL SERVER", bg="#7AB6FF", font=("courier"), relief="sunken")
    istruzioni.place(x=170,y=200, width=360)

    #textbox
    entry_host=tk.Entry(finestra, bg="#F2F2F2")
    entry_host.place(x=170,y=250, width=360)

    #avvio button
    button_host=tk.Button(finestra,text="AVVIO",bg="#7AB6FF",font=("courier"),command=avvio)
    button_host.place(x=320,y=300, width=60, height=40)

    scrollbarx = tk.Scrollbar(finestra,orient="horizontal")
    scrollbary = tk.Scrollbar(finestra)
    msg_list = tk.Listbox(finestra, height=15, width=50, bg="#F2F2F2", yscrollcommand=scrollbary.set,xscrollcommand=scrollbarx.set)
    scrollbary.config(command=msg_list.yview)
    scrollbarx.config(command=msg_list.xview)


    txt=tk.Label(finestra,text="PUNTEGGI:",font="courier",bg="#1e9856", relief="ridge")


    label_question=tk.Label(finestra,bg="#7AB6FF")

    a_button = tk.Button(finestra, command=lambda : risposta("A"), bg="#7AB6FF") 
    b_button = tk.Button(finestra, command=lambda : risposta("B"), bg="#7AB6FF")

    entry_field = tk.Entry(finestra, textvariable=my_msg, bg="#F2F2F2")
    entry_field.bind("<Return>", send)


    send_button = tk.Button(finestra, text="Invio", bg="#1e9856", command=send)


    comandi=[question,question,chiusura]

    q1_button = tk.Button(finestra, text="", command=comandi[0], bg="#1e9856") 
    q2_button = tk.Button(finestra, text="", command=comandi[1], bg="#1e9856") 
    t_button = tk.Button(finestra, text="", command=comandi[2], bg="#1e9856") 



    Classifica_Giocatori=tk.Label(finestra,text="giocatore ", font="courier" , bg="#1e9856", relief="sunken")


    disable_buttons()
    finestra.protocol("WM_DELETE_WINDOW", on_closing)

    BUFSIZ = 1024
    client_socket = socket(AF_INET, SOCK_STREAM)


    # avvia l'esecuzione della Finestra
    tk.mainloop()