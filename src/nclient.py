import socket
import json

from cow import *
from player import *
from tkinter import*
from _thread import start_new_thread
import sys

fen = Tk();
fen.title('CS COW');
fen.geometry("600x600");
fen.resizable(width = False, height = False);

mur=PhotoImage(file='mur.png')
piege=PhotoImage(file='piege.png')
soin=PhotoImage(file='soin.png')
route=PhotoImage(file='route.png')
noir=PhotoImage(file='warfog.png')
joueur=PhotoImage(file='player.png')

laby = None;
cow = None;
player = None;
ply = None;
canvas = None;

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

def test():
    while True:
        line = sys.stdin.readline()
        print(line);

start_new_thread(test, ());

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

def data(args):
    global laby;
    global cow;
    global player;
    global ply;

    laby = args[0];
    cow = Cow(args[1][0], args[1][1]);
    player = Player(Client);

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

        #canvas[ply.posY][ply.posX].create_image(20,20,image=joueur)

    # Fonction qui gere l'affichage du terrain au fur et a mesur de l'avancee du joueur.
    def joueurBrouillard(px, py):
        print("position de la fonction",px ,py)

        # Affichage du sol sous le joueur et le joueur lui meme.
        if labyrinthe[py][px] == 'T':
            canvas[py][px].create_image(20,20,image=piege)
        elif labyrinthe[py][px] == '.':
            canvas[py][px].create_image(20,20,image=route)
        elif labyrinthe[py][px] == 'H':
            canvas[py][px].create_image(20,20,image=soin)

        canvas[py][px].create_image(20,20,image=joueur)

        # Gestion et affichage des coordonees du joueur dans la fenetre de commande.
        print("position joueur", ply.posX, ply.posY)
        ply.posX = px
        ply.posY = py
        print("position joueur apres modification", ply.posX, ply.posY)

        Client.TriggerServerEvent("player:move", [ply.posX, ply.posY]);

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

    # Fonction qui gere le deplacement du joueur a partir des touches pressees et qui s'assure que le joueur ne peux pas avancer dans un mur.
    # Elle envoie ensuite les futures coordonees du joueur a "joueurBrouilard" pous qu'il soit affiche.
    def bouger(event):
        py = ply.posY
        px = ply.posX
        Key = repr(event.char)

        print("")
        print ('touche pressee :', Key)

        if Key == "'8'":
                if labyrinthe[int(py)-1][int(px)] == '#':
                    print("Mur en haut")
                else:
                    py = py-1
                    joueurBrouillard(px,py)

        elif Key == "'5'":
            if labyrinthe[int(py)+1][int(px)] == '#':
                print("Mur en bas")
            else:
                py = py+1
                joueurBrouillard(px,py) 

        elif Key == "'6'":
            if labyrinthe[int(py)][int(px)+1] == '#':
                print("Mur a droite")
            else:
                px = px+1
                joueurBrouillard(px,py)

        elif Key == "'4'":
            if labyrinthe[int(py)][int(px)-1] == '#':
                print("Mur a gauche")
            else:
                px = px-1
                joueurBrouillard(px,py)
        elif Key == "'-'":
            fullLaby()
        
        elif Key == "'\\x1b'":
            fen.destroy()

        elif Key =="'*'":
            initialisation(ply.posX, ply.posY)

        else :
            print("Mauvaise touche : \n 8 : Aller en haut \n 5 : Aller en bas \n 4 : Aller a gauche \n 6 : Aller a droite \n - : Afficher tout le labyrinthe \n * : Noircir tout le labyrinth \n echap : Quitter ")

    fen.bind("<Key>", bouger);
    joueurBrouillard(ply.posX, ply.posY)

Client.RegisterClientEvent("firstdata");
Client.AddEventHandler("firstdata", data);

def oplayerpos(args):
    global canvas;

    opos = args[0];
    print(opos)
    #canvas[opos[0]][opos[1]].create_image(20,20,image=joueur)

Client.RegisterClientEvent("oplayer:newpos");
Client.AddEventHandler("oplayer:newpos", oplayerpos);

def initd():
    global laby;
    global cow;
    global player;
    global Client;
    global ply;
    global canvas;

    # Creation d'un tableau de canvas vides pour y assigner plus facilement les images a l'aide des coordonees de celles ci.
    canvas = [[None for i in range(15)] for i in range(15)]

    # Creation de la classe player.
    class player:
        pass

    ply = player


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
    def initialisation(x, y):
        Brouillard()
        #fullLaby();
        setattr(ply, 'posX', x)
        setattr(ply, 'posY', y)
        canvas[ply.posY][ply.posX].create_image(20,20,image=joueur);
        fen.focus_set();

    # Une fonction pour affichr le labyrinthe complet avec le joueur.
    """ """

    initialisation(1, 1);
    #fen.update();
    fen.mainloop();

def stringToTbl():
    tbl = [["a" for i in range(15)] for i in range(15)]
    n=0
    for y in range(15):
        for x in range(15):
          tbl[y][x] = laby[n]
          n+=1
    return tbl

if __name__ == "__main__":
    initd();