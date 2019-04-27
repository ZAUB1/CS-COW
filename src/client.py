import socket
import json
import os

from cow import *
from player import *
from tkinter import *
from _thread import start_new_thread
from random import randint
import threading
import sys

from sound import playsound, ThreadedSound

fen = Tk();
fen.title('CS COW');
fen.geometry("600x600");
fen.resizable(width = False, height = False);

mur = PhotoImage(file = 'images/mur.png');
piege = PhotoImage(file = 'images/piege.png');
soin = PhotoImage(file = 'images/soin.png');
route = PhotoImage(file = 'images/route.png');
noir = PhotoImage(file = 'images/warfog.png');
joueur = PhotoImage(file = 'images/player.png');
joueur2 = PhotoImage(file = "images/player2.png");
cowi = PhotoImage(file = "images/cow.png");

#fen.iconbitmap("favicon.ico");

laby = None;
cow = None;
player = None;
canvas = None;
labyrinthe = None;
timevar = None;

lastplayer = [1, 1]; #Positions initiales des joueurs
lastoplayer = [1, 1];

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

def parsejson(data): #Fonction gérant la transformation de la chaine de caractères en objet et executant l'evenement correspondant
    data = json.loads(data);
    Client.TriggerInternalEvent(data['n'], data['args']);

def Main(): #Fonction principale du client
    address = "127.0.0.1"; #Addresse IP du serveur

    s = socket.socket(); #On crée le socket
    Client.connection = s; #On stocke la connection dans la classe Client
    s.connect((address, 120)); #On se connecte au serveur

    while True:
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
        if player.actions == 0:
            player.finishround(); #On fini le tour

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
    global timevar;

    if args[0] > 1:
        timevar.set("Temps restant : " + str(args[0]) + " secondes");
    else:
        timevar.set("Temps restant : 1 seconde");

Client.RegisterClientEvent("game:time");
Client.AddEventHandler("game:time", gametime);

# Fonction qui gere l'affichage du terrain au fur et a mesur de l'avancee du joueur.
def joueurBrouillard(px, py, oplayer):
    global canvas;
    global lastplayer;
    global lastoplayer;
    global player;
    global labyrinthe;

    labyrinthe = stringToTbl();

    # Affichage du sol sous le joueur et le joueur lui meme.
    if labyrinthe[py][px] == 'T':
        canvas[py][px].create_image(20, 20, image = piege);
    elif labyrinthe[py][px] == '.':
        canvas[py][px].create_image(20, 20, image = route);
    elif labyrinthe[py][px] == 'H':
        canvas[py][px].create_image(20, 20, image = soin);

    if oplayer == True:
        canvas[py][px].create_image(20, 20, image = joueur);
    else:
        canvas[py][px].create_image(20, 20, image = joueur2);

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

        if labyrinthe[cy][cx] == '#':
            canvas[cy][cx].create_image(20, 20, image = mur);
        elif labyrinthe[cy][cx] == 'T':
            canvas[cy][cx].create_image(20, 20, image = piege);
        elif labyrinthe[cy][cx] == '.':
            canvas[cy][cx].create_image(20, 20, image = route);
        elif labyrinthe[cy][cx] == 'H':
            canvas[cy][cx].create_image(20, 20, image = soin);

        if (cow.pos.x == cx) and (cow.pos.y == cy):
            player.win();
            canvas[cow.pos.y][cow.pos.x].create_image(20, 20, image = cowi);

    if oplayer == True:
        canvas[lastplayer[1]][lastplayer[0]].create_image(20, 20, image = joueur2);
    else:
        canvas[lastoplayer[1]][lastoplayer[0]].create_image(20, 20, image = joueur);

def data(args): #Fonction executée dès lors de la reception des données initiales par le serveur (contenant le labyrinthe, la position de la vache, etc ..)
    global laby;
    global cow;
    global player;
    global lastplayer;
    global timevar;

    laby = args[0];
    # Assignation du tableau a "labyrinthe".
    labyrinthe = stringToTbl();

    cow = Cow(args[1][0], args[1][1]);
    player.SetClient(Client, args[2], labyrinthe);

    stats = StringVar();
    statslab = Label(fen, textvariable = stats);
    statslab.place(x = 5, y = 5);

    player.SetTxt(stats);
    stats.set("Vie: " + str(10) + " | Joueurs connectés: " + str(args[2]) + " | En attente de joueur");

    timevar = StringVar();
    timelab = Label(fen, textvariable = timevar);
    timelab.place(x = 5, y = 570);

    timevar.set("Temps restant : 300 secondes");

    # Fonction qui gere le deplacement du joueur a partir des touches pressees et qui s'assure que le joueur ne peux pas avancer dans un mur.
    # Elle envoie ensuite les futures coordonees du joueur a "joueurBrouilard" pous qu'il soit affiche.
    def bouger(event):
        global lastplayer;

        py = player.pos.y;
        px = player.pos.x;
        Key = repr(event.char);

        if Key == "'z'":
            if labyrinthe[int(py) - 1][int(px)] != '#':
                py = py - 1;
        elif Key == "'s'":
            if labyrinthe[int(py) + 1][int(px)] != '#':
                py = py + 1;
        elif Key == "'d'":
            if labyrinthe[int(py)][int(px) + 1] != '#':
                px = px + 1;
        elif Key == "'q'":
            if labyrinthe[int(py)][int(px) - 1] != '#':
                px = px - 1;

        if (player.freeze == False) and ((player.pos.x != px) or (player.pos.y != py)): #On verifie que le joueur peut bouger et que sa position à bien changée
            if labyrinthe[int(py)][int(px)] == "T": #Handle trap catch
                print("Player on trap");
                player.FreezePos(True);
                player.setlife(player.life - 2);
                player.updateinfo();
                player.finishround();
            elif labyrinthe[int(py)][int(px)] == "H": #Handle heal
                print("Player on heal");
                player.setlife(player.life + 2);
                player.updateinfo();
                labyrinthe[int(py)][int(px)] = ".";
                canvas[int(px)][int(py)].create_image(20, 20, image = route);

            player.move(px, py); #On déplace le joueur
            lastplayer = [px, py]; #On sauvegarde la dernière position
            joueurBrouillard(px, py, False);
            ThreadedSound("./sounds/walk.mp3"); #On émet un son dès lors que le joueur bouge

    fen.bind("<Key>", bouger);
    joueurBrouillard(player.pos.x, player.pos.y, False);
    start_new_thread(actionsgest, ()); #On execute la gestion des actions réstante de manière séparée pour ne pas bloquer le reste du programme

Client.RegisterClientEvent("firstdata");
Client.AddEventHandler("firstdata", data);

def ConnectedUpdate(args): #Fonction permettant simplement d'informer le joueur qu'un autre s'est connecté
    global player;
    player.AddConnected();

Client.RegisterClientEvent("oplayer:connected");
Client.AddEventHandler("oplayer:connected", ConnectedUpdate);

def oplayerpos(args): #Fonction gérant l'actualisation de la position de l'autre joueur
    global canvas;
    global lastoplayer;

    opos = args[0];
    lastoplayer = [opos[0], opos[1]];
    joueurBrouillard(opos[0], opos[1], True);

Client.RegisterClientEvent("oplayer:newpos");
Client.AddEventHandler("oplayer:newpos", oplayerpos);

def revealmap(args):
    global labyrinthe;
    global canvas;
    global cow;

    for Y in range(15):
        for X in range(15):
            if labyrinthe[Y][X] == '#':
                canvas[Y][X].create_image(20, 20, image = mur);

            elif labyrinthe[Y][X] == ".":
                canvas[Y][X].create_image(20, 20, image = route);

            elif labyrinthe[Y][X] == "T":
                canvas[Y][X].create_image(20, 20, image = piege);

            elif labyrinthe[Y][X] == "H":
                canvas[Y][X].create_image(20, 20, image = soin);

    canvas[cow.pos.y][cow.pos.x].create_image(20, 20, image = cowi);

def revmapthr(args): #Fonction permettant de releveler la totalité du labyrinthe à la fin de la partie
    start_new_thread(revealmap, (args, ));

Client.RegisterClientEvent("players:reveal");
Client.AddEventHandler("players:reveal", revmapthr);

def initd(): #Fonction initiale du programme
    global laby;
    global cow;
    global player;
    global Client;
    global canvas;

    # Creation d'un tableau de canvas vides pour y assigner plus facilement les images a l'aide des coordonees de celles ci.
    canvas = [[None for i in range(15)] for i in range(15)]

    player = Player(fen); #On crée le joueur

    # On positionne tout les canvas sur la fenetre
    for Y in range(15):
        for X in range(15):
            canvas[Y][X] = Canvas(fen);
            canvas[Y][X].place(x = (40 * X), y = (40 * Y), width = 40, height = 40, anchor = NW);

    # On rempli tous les canvas d'une image noir pour cacher le labyrinthe.
    def Brouillard():
        for Y in range(15):
            for X in range(15):
                canvas[Y][X].create_image(20, 20, image = noir);

    # fonction pour initialiser la classe "player" creer "posX" et "posY" qui seront les coordonees de ce dernier.
    # On place le joueur et on decouvre le labyrinthe grace a "joueurBrouillard".
    def initialisation():
        Brouillard();

        canvas[player.pos.y][player.pos.x].create_image(20, 20, image = joueur);
        fen.focus_set();

    initialisation();
    fen.mainloop(); #Boucle de Tkinter

def stringToTbl(): #Fonction transformant la chaine de caractères du labyrinthe reçue en tableau 2D
    tbl = [["a" for i in range(15)] for i in range(15)];
    n = 0;
    for y in range(15):
        for x in range(15):
            tbl[y][x] = laby[n];
            n += 1;
    return tbl

if __name__ == "__main__": #On verifie que le programme n'est pas executé en tant que module d'un autre
    initd();