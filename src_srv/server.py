import socket
import sys
from _thread import start_new_thread
import threading
import json
import os
import asyncio

from map import *
from player import *
from game import *

HOST = "";
PORT = 120; #Definition du port à contacter pour se connecter au serveur

g_conn = None;
g_players = {};

g_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); #Création du serveur avec le protocole de sockets
g_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);

g_map = genLaby(); #Generation du labyrinthe
g_cow = Cow(g_map); #Creation de la vache

def setInterval(func, time): #Fonction permettant d'executer toutes les n secondes une autre fonction
    e = threading.Event();
    while not e.wait(time):
        func();

class QItem: #Classe permettant de creer un objet à envoyer depuis le serveur
    def __init__(self, client, stri):
        self.client = client;
        self.stri = stri;

class SrvEvents: #Classe principale du serveur
    def __init__(self):
        self.sevents = {};
        self.conns = [];
        self.connsbyid = {};
        self.lastsource = None;
        self.lastid = None;
        self.queued = []; #File d'attente pour envoyer les evenements

        start_new_thread(self.startsendloop, ());

    def sendloop(self): #Méthode executée dans un intervalle gérant l'envoi differé des evenements au clients
        if len(self.queued) > 0: #On verifie qu'il y a des evenements dans la file d'attente
            print(self.queued[0].stri);
            self.queued[0].client.send(bytes(self.queued[0].stri, "utf-8"));
            del self.queued[0];

    def startsendloop(self):
        setInterval(self.sendloop, 0.2); #Lancement de l'intervalle pour gerer l'envoi des evenements

    def addtosend(self, client, stri): #Méthode ajoutant un evenement à la file d'attente
        self.queued.append(QItem(client, stri));

    def RegisterServerEvent(self, n): #Méthode qui déclare un nouvel evevenement sur le serveur
        self.sevents[n] = None;

    def TriggerIntervalEvent(self, n, args): #Méthode qui execute un evenement interne au serveur
        self.sevents[n](args);

    def AddEventHandler(self, n, cb): #Méthode qui affecte une fonction de rappel à un evenement
        self.sevents[n] = cb;

    def TriggerGlobalClientEvent(self, n, *args): #Méthode qui execute un evenement sur tous les clients
        arr = [];

        for i in args:
            arr.append(i);

        for i in range(len(self.conns)):
            self.addtosend(self.conns[i], json.dumps({"n": n, "args": arr}));

    def TriggerClientEvent(self, client, n, *args): #Méthode qui execute un evenement sur le client spécifié
        arr = [];

        for i in args:
            arr.append(i);

        self.addtosend(client, json.dumps({"n": n, "args": arr}));

    def SendAllExcept(self, n, client, *args): #Méthode qui execute un evenement sur tous les clients sauf celui spécifié
        arr = [];

        for i in args:
            arr.append(i);

        for i in range(len(self.conns)):
            if (self.conns[i].getpeername()[1] != client) == True:
                self.addtosend(self.conns[i], json.dumps({"n": n, "args": arr}));

    def GetLastSource(self): #Méthode qui retourne le dernier client à avoir envoyé au serveur
        return self.lastsource;

    def GetLastId(self): #Méthode qui retourne l'indentifiant du dernier client à avoir envoyé au serveur
        return self.lastid;

Server = SrvEvents(); #Création de la classe serveur

game = Game(Server); #Création de la partie

print(":: Socket Created");

g_s.bind((HOST, PORT)); #On affecte le socket au port souhaité
print(":: Socket port " + str(PORT));

g_s.listen(0); #On lance l'ecoute de connection
print(":: Listening...");

def prompt(): #Fonction gérant les entrées dans la console serveur
    while True:
        line = sys.stdin.readline()

        if "clist" in line:
            for i in range(len(Server.conns)):
                print(i + 1, "- id:", str(Server.conns[i].getpeername()[1]) + ",", "ip:", Server.conns[i].getpeername()[0]);
        elif "exit" in line:
            os._exit(1)

start_new_thread(prompt, ()); #On lance la fonction dans un autre thread que le principal

def client_thread(conn, addr): #Fonction gérant la connection d'un client
    Server.TriggerClientEvent(conn, "connected");

    if len(Server.conns) > 1: #On lance la partie si il y a plus d'un joueur
        Server.SendAllExcept("oplayer:connected", conn.getpeername()[1]);
        game.start();

    while True:
        data = conn.recv(1024); #On receptionne les données du client
        data = data.decode("UTF-8"); #On converties les données recues dans le bon format

        if not data:
            break; #On ferme la connection dans le cas ou le client serait quitté de manière imprevue
        else:
            data = json.loads(data); #On transforme la chaine de caractères en objet
            Server.lastsource = conn; #On affecte la dernière source
            Server.lastid = conn.getpeername()[1]; #On affecte le dernier identifiant du joueur (unique puisqu'il s'agit du port utilisé pour le lien)

            Server.TriggerIntervalEvent(data['n'], data['args']); #On execute l'evenement correspondant au n

    Server.conns.remove(conn); #On enleve le joueur des connectés
    conn.close(); #On ferme la connection

    print("-> Disconnected from " + addr[0] + ":" + str(addr[1]));

def srvloop(): #Fonction principale permettant de prendre en charge la connection d'un joueur
    while True:
        conn, addr = g_s.accept(); #On accepte la connection
        Server.conns.append(conn); #On ajoute la connection parmis les connectés

        print("-> Connected to " + addr[0] + ":" + str(addr[1]));

        start_new_thread(client_thread, (conn, addr, )); #On lance le client dans un thread de manière à l'executer séparement du programme principal

async def OnClientConnected(args): #Fonction executée lors du pong (retour du client à la suite de la connection)
    g_players[Server.GetLastId()] = Player(); #On ajoute le client à la liste des joueurs

    await asyncio.sleep(0.5);
    Server.TriggerClientEvent(Server.GetLastSource(), "firstdata", MaptoString(g_map), g_cow.pos.coords(), len(Server.conns)); #On envoi la carte, la position de la vache ainsi que le nombre de joueur connectés au client.

def handleconnection(args):
    asyncio.run(OnClientConnected(args)); #On execute la fonction de manière asynchrone afin de pouvoir attendre un certain temps sans bloquer le reste du programme

Server.AddEventHandler("onclientconnected", handleconnection);

#Player events

async def sendnewpos(): #Fonction gérant l'envoi de la position d'un joueur lors de son déplacement aux autres joueurs
    await asyncio.sleep(0.05);
    Server.SendAllExcept("oplayer:newpos", Server.GetLastId(), g_players[Server.GetLastId()].pos.coords());

def moveply(args):
    g_players[Server.GetLastId()].pos.Set(args[0][0], args[0][1]); #On stocke la position du joueur
    asyncio.run(sendnewpos()); #On execute la fonction de manière asynchrone afin de pouvoir attendre un certain temps sans bloquer le reste du programme

Server.AddEventHandler("player:move", moveply);

def wingame(args): #Fonction executée lorsque la partie est gagnée.
    Server.TriggerGlobalClientEvent("players:reveal");
    Server.SendAllExcept("game:winpop", Server.GetLastId());

Server.RegisterServerEvent("game:win");
Server.AddEventHandler("game:win", wingame);

srvloop(); #On lance la boucle du serveur