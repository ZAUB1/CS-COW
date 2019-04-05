import socket
import json

from cow import *
from player import *
from tkinter import *
from _thread import start_new_thread
import sys

fen = Tk();
fen.title('CS COW');
fen.geometry("600x600");
fen.resizable(width = False, height = False);

mur=PhotoImage(file='mur.png');
piege=PhotoImage(file='piege.png');
soin=PhotoImage(file='soin.png');
route=PhotoImage(file='route.png');
noir=PhotoImage(file='warfog.png');
joueur=PhotoImage(file='player.png');
cowi = PhotoImage(file="cow.png");

laby = None;
cow = None;
player = None;
canvas = None;

lastplayer = [1, 1];
lastoplayer = [1, 1];

class ClientEvent:
    def __init__(self):
        self.events = {};
        self.connection = None;

    def RegisterClientEvent(self, n):
        self.events[n] = None;

    def AddEventHandler(self, n, cb):
        self.events[n] = cb;

    def TriggerInternalEvent(self, n, args):
        self.events[n](args);

    def TriggerServerEvent(self, n, *args):
        arr = [];

        for i in args:
            arr.append(i);

        self.connection.send(bytes(json.dumps({"n": n, "args": arr}), 'utf-8'));

Client = ClientEvent();

def Main():
    address = "127.0.0.1";

    s = socket.socket();
    Client.connection = s;
    s.connect((address, 120));

    while True:
        data = s.recv(1024);
        data = data.decode("UTF-8");

        if not data:
            break;
        else:
            data = json.loads(data);
            Client.TriggerInternalEvent(data['n'], data['args']);

    s.close();

start_new_thread(Main, ());

def OnConnected(args):
    print("-> Connected to server");
    Client.TriggerServerEvent("onclientconnected");

Client.RegisterClientEvent("connected");
Client.AddEventHandler("connected", OnConnected);

def OPlayerRdy(args):
    global player;
    player.FreezePos(False);

Client.RegisterClientEvent("oplayer:connected");
Client.AddEventHandler("oplayer:connected", OPlayerRdy);

# Fonction qui gere l'affichage du terrain au fur et a mesur de l'avancee du joueur.
def joueurBrouillard(px, py, oplayer):
    global canvas;
    global lastplayer;
    global lastoplayer;

    labyrinthe = stringToTbl();

    # Affichage du sol sous le joueur et le joueur lui meme.
    if labyrinthe[py][px] == 'T':
        canvas[py][px].create_image(20,20,image=piege)
    elif labyrinthe[py][px] == '.':
        canvas[py][px].create_image(20,20,image=route)
    elif labyrinthe[py][px] == 'H':
        canvas[py][px].create_image(20,20,image=soin)

    canvas[py][px].create_image(20,20,image=joueur)

    # Gestion de la vision du joueur autour de sa case.
    for i in range(4):
        if i == 0:
            cx = px-1
            cy = py
        elif i == 1:
            cx = px+1
            cy = py
        elif i == 2:
            cx = px
            cy = py-1
        elif i == 3:
            cx = px
            cy = py+1

        if labyrinthe[cy][cx] == '#':
            canvas[cy][cx].create_image(20,20,image=mur)
        elif labyrinthe[cy][cx] == 'T':
            canvas[cy][cx].create_image(20,20,image=piege)
        elif labyrinthe[cy][cx] == '.':
            canvas[cy][cx].create_image(20,20,image=route)
        elif labyrinthe[cy][cx] == 'H':
            canvas[cy][cx].create_image(20,20,image=soin)

        if (cow.pos.x == cx) and (cow.pos.y == cy):
            print("Won");
            canvas[cow.pos.y][cow.pos.x].create_image(20,20,image=cowi);

    if oplayer == True:
        canvas[lastplayer[1]][lastplayer[0]].create_image(20,20,image=joueur);
    else:
        canvas[lastoplayer[1]][lastoplayer[0]].create_image(20,20,image=joueur);

def data(args):
    global laby;
    global cow;
    global player;
    global lastplayer;

    laby = args[0];
    cow = Cow(args[1][0], args[1][1]);
    player.SetClient(Client);

    # Assignation du tableau a "labyrinthe".
    labyrinthe = stringToTbl();

    def fullLaby():
        for Y in range(15):
            for X in range(15):
                if labyrinthe[Y][X] == '#':
                    canvas[Y][X].create_image(20,20,image=mur)

                elif labyrinthe[Y][X] == ".":
                    canvas[Y][X].create_image(20,20,image=route)

                elif labyrinthe[Y][X] == "T":
                    canvas[Y][X].create_image(20,20,image=piege)

                elif labyrinthe[Y][X] == "H":
                    canvas[Y][X].create_image(20,20,image=soin)

        #canvas[player.pos.y][player.pos.x].create_image(20,20,image=joueur)

    # Fonction qui gere le deplacement du joueur a partir des touches pressees et qui s'assure que le joueur ne peux pas avancer dans un mur.
    # Elle envoie ensuite les futures coordonees du joueur a "joueurBrouilard" pous qu'il soit affiche.
    def bouger(event):
        global lastplayer;

        py = player.pos.y
        px = player.pos.x
        Key = repr(event.char)

        if Key == "'z'":
            if labyrinthe[int(py)-1][int(px)] != '#':
                py = py-1
        elif Key == "'s'":
            if labyrinthe[int(py)+1][int(px)] != '#':
                py = py+1
        elif Key == "'d'":
            if labyrinthe[int(py)][int(px)+1] != '#':
                px = px+1
        elif Key == "'q'":
            if labyrinthe[int(py)][int(px)-1] != '#':
                px = px-1

        if (player.freeze == False):
            player.move(px, py);
            lastplayer = [px, py];
            joueurBrouillard(px, py, False);

    fen.bind("<Key>", bouger);
    joueurBrouillard(player.pos.x, player.pos.y, False)

Client.RegisterClientEvent("firstdata");
Client.AddEventHandler("firstdata", data);

def oplayerpos(args):
    global canvas;
    global lastoplayer;

    opos = args[0];
    lastoplayer = [opos[0], opos[1]];
    joueurBrouillard(opos[0], opos[1], True);

Client.RegisterClientEvent("oplayer:newpos");
Client.AddEventHandler("oplayer:newpos", oplayerpos);

def initd():
    global laby;
    global cow;
    global player;
    global Client;
    global canvas;

    # Creation d'un tableau de canvas vides pour y assigner plus facilement les images a l'aide des coordonees de celles ci.
    canvas = [[None for i in range(15)] for i in range(15)]

    player = Player();

    # On positionne tout les canvas sur la fenetre
    for Y in range(15):
        for X in range(15):
            canvas[Y][X]=Canvas(fen)
            canvas[Y][X].place(x=(40*X),y=(40*Y), width=40, height=40,anchor=NW)

    # On rempli tous les canvas d'une image noir pour cacher le labyrinthe.
    def Brouillard():
        for Y in range(15):
            for X in range(15):
                canvas[Y][X].create_image(20,20,image=noir)

    # fonction pour initialiser la classe "player" creer "posX" et "posY" qui seront les coordonees de ce dernier.
    # On place le joueur et on decouvre le labyrinthe grace a "joueurBrouillard".
    def initialisation():
        Brouillard()

        canvas[player.pos.y][player.pos.x].create_image(20,20,image=joueur);
        fen.focus_set();

    initialisation();
    fen.mainloop();

def stringToTbl():
    tbl = [["a" for i in range(15)] for i in range(15)];
    n = 0;
    for y in range(15):
        for x in range(15):
            tbl[y][x] = laby[n];
            n += 1;
    return tbl

if __name__ == "__main__":
    initd();