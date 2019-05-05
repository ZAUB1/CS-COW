import socket
import json
import os

from cow import *
from player import *
from discord import DPresence
from tkinter import *
from _thread import start_new_thread
from random import randint
import threading
import sys

from sound import playsound, ThreadedSound

g_address = "127.0.0.1"; #Addresse IP du serveur

g_fen = Tk();
g_fen.title('CS COW');
g_fen.geometry("600x600");
g_fen.resizable(width = False, height = False);

g_mur = PhotoImage(file = 'images/mur.png');
g_piege = PhotoImage(file = 'images/piege.png');
g_soin = PhotoImage(file = 'images/soin.png');
g_route = PhotoImage(file = 'images/route.png');
g_noir = PhotoImage(file = 'images/warfog.png');
g_joueur = PhotoImage(file = 'images/player.png');
g_joueur2 = PhotoImage(file = "images/player2.png");
g_cowi = PhotoImage(file = "images/cow.png");

DPresence();

#g_fen.iconbitmap("favicon.ico");

g_laby = None;
g_cow = None;
g_player = None;
g_canvas = None;
g_labyrinthe = None;
g_timevar = None;

g_isTimed = False;

g_lastPlayer = [1, 1]; #Positions initiales des joueurs
g_lastOPlayer = [1, 1];

def setInterval(func, time): #Fonction permettant d'executer toutes les n secondes une autre fonction
    e = threading.Event();
    while not e.wait(time):
        func();

class ClientEvent: #Classe principale du client
    def __init__(self):
        self.events = {};
        self.connection = None;

    def RegisterClientEvent(self, n): #Méthode qui déclare un nouvel evevenement sur le client
        self.events[n] = None;

    def AddEventHandler(self, n, cb): #Méthode qui affecte une fonction de rappel à un evenement
        self.events[n] = cb;

    def TriggerInternalEvent(self, n, args): #Méthode qui execute un evenement interne au client
        self.events[n](args);

    def TriggerServerEvent(self, n, *args): #Méthode qui execute un evenement sur le serveur
        arr = [];

        for i in args:
            arr.append(i);

        self.connection.send(bytes(json.dumps({"n": n, "args": arr}), 'utf-8'));

Client = ClientEvent(); #Création du client

def prompt(): #Fonction gérant les entrées dans la console serveur
    global g_address;

    while True:
        line = sys.stdin.readline()

        if "connect" in line:
            ipentered = "";

            for i in range(8, len(line) - 1):
                ipentered += str(line[i]);

            g_address = ipentered;
            start_new_thread(Main, ());
        elif "exit" in line:
            os._exit(1)

start_new_thread(prompt, ()); #On lance la fonction dans un autre thread que le principal

def parsejson(data): #Fonction gérant la transformation de la chaine de caractères en objet et executant l'evenement correspondant
    data = json.loads(data);
    Client.TriggerInternalEvent(data['n'], data['args']);

def Main(): #Fonction principale du client
    connected = False

    s = socket.socket(); #On crée le socket
    Client.connection = s; #On stocke la connection dans la classe Client

    try:
        s.connect((g_address, 120)); #On se connecte au serveur
        connected = True;
    except Exception as e:
        e = str(e);
        if "111" in e:
            print("Can't connect to server, is the IP right ? (if not local IP type 'connect YOUR_IP' in the client console");

    while True:
        if connected == True:
            data = s.recv(1024); #On receptionne les données du client
            data = data.decode("UTF-8"); #On converties les données recues dans le bon format

            if not data:
                os._exit(1); #Si le serveur est indisponible ou coupé on ferme de force le client
                break;
            else:
                start_new_thread(parsejson, (data, )); #On execute de manière séparée la gestion de l'evenement

    s.close(); #On ferme la connection si le programme est quittée

start_new_thread(Main, ()); #On execute la connection au serveur séparement pour ne pas bloquer Tkinter

def actionsgest(): #Fonction verifiant si le joueur a effectué toutes ses actions disponibles et finissant le tour automatiquement le cas échéantg
    while True:
        if g_player.actions == 0:
            g_player.finishround(); #On fini le tour

def OnConnected(args): #Fonction executée dès lors que la connection au serveur est établie
    print("-> Connected to server");
    Client.TriggerServerEvent("onclientconnected"); #On envoi au serveur le pong (retour de connection)

Client.RegisterClientEvent("connected");
Client.AddEventHandler("connected", OnConnected);

def cownoise(): #Fonction qui aléatoirement emet un bruit de vache
    ri = randint(0, 3);

    if ri == 3:
        ThreadedSound("./sounds/cow.mp3"); #On emet le son

def gamestarted(args): #Fonction executée dès lors qu'une partie à commencé
    setInterval(cownoise, 10);

Client.RegisterClientEvent("game:started");
Client.AddEventHandler("game:started", gamestarted);

def gametime(args): #Fonction métant à jour le temps de la partie en cours
    global g_timevar;
    global g_isTimed;

    if g_isTimed == True:
        if args[0] > 1:
            g_timevar.set("Temps restant : " + str(args[0]) + " secondes");
        else:
            g_timevar.set("Temps restant : 1 seconde");

Client.RegisterClientEvent("game:time");
Client.AddEventHandler("game:time", gametime);

# Fonction qui gere l'affichage du terrain au fur et a mesur de l'avancee du joueur.
def joueurBrouillard(px, py, oplayer):
    global g_canvas;
    global g_lastPlayer;
    global g_lastOPlayer;
    global g_player;
    global g_labyrinthe;

    g_labyrinthe = stringToTbl();

    # Affichage du sol sous le joueur et le joueur lui meme.
    if g_labyrinthe[py][px] == 'T':
        g_canvas[py][px].create_image(20, 20, image = g_piege);
    elif g_labyrinthe[py][px] == '.':
        g_canvas[py][px].create_image(20, 20, image = g_route);
    elif g_labyrinthe[py][px] == 'H':
        g_canvas[py][px].create_image(20, 20, image = g_soin);

    if oplayer == True:
        g_canvas[py][px].create_image(20, 20, image = g_joueur);
    else:
        g_canvas[py][px].create_image(20, 20, image = g_joueur2);

    # Gestion de la vision du joueur autour de sa case.
    for i in range(4):
        if i == 0:
            cx = px - 1;
            cy = py;
        elif i == 1:
            cx = px + 1;
            cy = py;
        elif i == 2:
            cx = px;
            cy = py - 1;
        elif i == 3:
            cx = px;
            cy = py + 1;

        if g_labyrinthe[cy][cx] == '#':
            g_canvas[cy][cx].create_image(20, 20, image = g_mur);
        elif g_labyrinthe[cy][cx] == 'T':
            g_canvas[cy][cx].create_image(20, 20, image = g_piege);
        elif g_labyrinthe[cy][cx] == '.':
            g_canvas[cy][cx].create_image(20, 20, image = g_route);
        elif g_labyrinthe[cy][cx] == 'H':
            g_canvas[cy][cx].create_image(20, 20, image = g_soin);

        if (g_cow.pos.x == cx) and (g_cow.pos.y == cy):
            g_player.win();
            g_canvas[g_cow.pos.y][g_cow.pos.x].create_image(20, 20, image = cowi);

    if oplayer == True:
        g_canvas[g_lastPlayer[1]][g_lastPlayer[0]].create_image(20, 20, image = g_joueur2);
    else:
        g_canvas[g_lastOPlayer[1]][g_lastOPlayer[0]].create_image(20, 20, image = g_joueur);

def data(args): #Fonction executée dès lors de la reception des données initiales par le serveur (contenant le labyrinthe, la position de la vache, etc ..)
    global g_laby;
    global g_cow;
    global g_player;
    global g_lastPlayer;
    global g_timevar;
    global g_isTimed;

    g_laby = args[0];
    # Assignation du tableau a "labyrinthe".
    g_labyrinthe = stringToTbl();

    g_cow = Cow(args[1][0], args[1][1]);
    g_player.SetClient(Client, args[2], g_labyrinthe);

    stats = StringVar();
    statslab = Label(g_fen, textvariable = stats);
    statslab.place(x = 5, y = 5);

    g_player.SetTxt(stats);
    stats.set("Vie: " + str(10) + " | Joueurs connectés: " + str(args[2]) + " | En attente de joueur");

    g_timevar = StringVar();
    timelab = Label(g_fen, textvariable = g_timevar);
    timelab.place(x = 5, y = 570);

    g_timevar.set("Temps restant : 300 secondes");
    g_isTimed = True;

    # Fonction qui gere le deplacement du joueur a partir des touches pressees et qui s'assure que le joueur ne peux pas avancer dans un mur.
    # Elle envoie ensuite les futures coordonees du joueur a "joueurBrouilard" pous qu'il soit affiche.
    def bouger(event):
        global g_lastPlayer;

        py = g_player.pos.y;
        px = g_player.pos.x;
        Key = repr(event.char);

        if Key == "'z'":
            if g_labyrinthe[int(py) - 1][int(px)] != '#':
                py = py - 1;
        elif Key == "'s'":
            if g_labyrinthe[int(py) + 1][int(px)] != '#':
                py = py + 1;
        elif Key == "'d'":
            if g_labyrinthe[int(py)][int(px) + 1] != '#':
                px = px + 1;
        elif Key == "'q'":
            if g_labyrinthe[int(py)][int(px) - 1] != '#':
                px = px - 1;

        if (g_player.freeze == False) and ((g_player.pos.x != px) or (g_player.pos.y != py)): #On verifie que le joueur peut bouger et que sa position à bien changée
            if g_labyrinthe[int(py)][int(px)] == "T": #Handle trap catch
                print("Player on trap");
                g_player.FreezePos(True);
                g_player.setlife(g_player.life - 2);
                g_player.updateinfo();
                g_player.finishround();
            elif g_labyrinthe[int(py)][int(px)] == "H": #Handle heal
                print("Player on heal");
                g_player.setlife(g_player.life + 2);
                g_player.updateinfo();
                g_labyrinthe[int(py)][int(px)] = ".";
                g_canvas[int(py)][int(px)].create_image(20, 20, image = g_route);

            g_player.move(px, py); #On déplace le joueur
            g_lastPlayer = [px, py]; #On sauvegarde la dernière position
            joueurBrouillard(px, py, False);
            ThreadedSound("./sounds/walk.mp3"); #On émet un son dès lors que le joueur bouge

    g_fen.bind("<Key>", bouger);
    joueurBrouillard(g_player.pos.x, g_player.pos.y, False);
    start_new_thread(actionsgest, ()); #On execute la gestion des actions réstante de manière séparée pour ne pas bloquer le reste du programme

Client.RegisterClientEvent("firstdata");
Client.AddEventHandler("firstdata", data);

def ConnectedUpdate(args): #Fonction permettant simplement d'informer le joueur qu'un autre s'est connecté
    global g_player;
    g_player.AddConnected();

Client.RegisterClientEvent("oplayer:connected");
Client.AddEventHandler("oplayer:connected", ConnectedUpdate);

def oplayerpos(args): #Fonction gérant l'actualisation de la position de l'autre joueur
    global g_canvas;
    global g_lastOPlayer;

    opos = args[0];
    g_lastOPlayer = [opos[0], opos[1]];
    joueurBrouillard(opos[0], opos[1], True);

Client.RegisterClientEvent("oplayer:newpos");
Client.AddEventHandler("oplayer:newpos", oplayerpos);

def revealmap(args):
    global g_labyrinthe;
    global g_canvas;
    global g_cow;

    for Y in range(15):
        for X in range(15):
            if g_labyrinthe[Y][X] == '#':
                g_canvas[Y][X].create_image(20, 20, image = g_mur);

            elif g_labyrinthe[Y][X] == ".":
                g_canvas[Y][X].create_image(20, 20, image = g_route);

            elif g_labyrinthe[Y][X] == "T":
                g_canvas[Y][X].create_image(20, 20, image = g_piege);

            elif g_labyrinthe[Y][X] == "H":
                g_canvas[Y][X].create_image(20, 20, image = g_soin);

    g_canvas[g_cow.pos.y][g_cow.pos.x].create_image(20, 20, image = cowi);

def revmapthr(args): #Fonction permettant de releveler la totalité du labyrinthe à la fin de la partie
    start_new_thread(revealmap, (args, ));

Client.RegisterClientEvent("players:reveal");
Client.AddEventHandler("players:reveal", revmapthr);

def initd(): #Fonction initiale du programme
    global g_laby;
    global g_cow;
    global g_player;
    global Client;
    global g_canvas;

    # Creation d'un tableau de canvas vides pour y assigner plus facilement les images a l'aide des coordonees de celles ci.
    g_canvas = [[None for i in range(15)] for i in range(15)]

    g_player = Player(g_fen); #On crée le joueur

    # On positionne tout les canvas sur la fenetre
    for Y in range(15):
        for X in range(15):
            g_canvas[Y][X] = Canvas(g_fen);
            g_canvas[Y][X].place(x = (40 * X), y = (40 * Y), width = 40, height = 40, anchor = NW);

    # On rempli tous les canvas d'une image noir pour cacher le labyrinthe.
    def Brouillard():
        for Y in range(15):
            for X in range(15):
                g_canvas[Y][X].create_image(20, 20, image = g_noir);

    # fonction pour initialiser la classe "player" creer "posX" et "posY" qui seront les coordonees de ce dernier.
    # On place le joueur et on decouvre le labyrinthe grace a "joueurBrouillard".
    def initialisation():
        Brouillard();

        g_canvas[g_player.pos.y][g_player.pos.x].create_image(20, 20, image = g_joueur);
        g_fen.focus_set();

    initialisation();
    g_fen.mainloop(); #Boucle de Tkinter

def stringToTbl(): #Fonction transformant la chaine de caractères du labyrinthe reçue en tableau 2D
    tbl = [["a" for i in range(15)] for i in range(15)];
    n = 0;
    for y in range(15):
        for x in range(15):
            tbl[y][x] = g_laby[n];
            n += 1;
    return tbl

if __name__ == "__main__": #On verifie que le programme n'est pas executé en tant que module d'un autre
    initd();