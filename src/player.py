from vector import Vector2
from tkinter import *

class Player:
    def __init__(self):
        self.pos = Vector2(1, 1);
        self.life = 10;
        self.actions = 2;

        self.Client = None;
        self.freeze = True;
        self.stats = None;
        self.connectedplayers = None;

        self.rostr = "C'est au tour de l'autre joueur";

    def move(self, x, y):
        self.pos.x = x;
        self.pos.y = y;

        self.actions -= 1;

        self.Client.TriggerServerEvent("player:move", self.pos.coords());

    def setlife(self, life):
        self.life = life;
        self.updateinfo();

    def SetClient(self, cl, connecteds):
        self.Client = cl;
        self.connectedplayers = connecteds;

        self.Client.RegisterClientEvent("game:turn");
        self.Client.AddEventHandler("game:turn", self.startround);

        self.Client.RegisterClientEvent("game:winpop");
        self.Client.AddEventHandler("game:winpop", self.winpop);

    def AddConnected(self):
        self.connectedplayers += 1;
        self.updateinfo();

    def SetTxt(self, str):
        self.stats = str;

    def FreezePos(self, st):
        self.freeze = st;

    def startround(self, shit):
        self.freeze = False;
        self.rostr = "C'est votre tour de jouer";
        self.updateinfo();

    def finishround(self):
        self.Client.TriggerServerEvent("player:endround");
        self.freeze = True;
        self.actions = 2;
        self.rostr = "C'est au tour de l'autre joueur";
        self.updateinfo();

    def updateinfo(self):
        self.stats.set("Vie: " + str(self.life) + " | Joueurs connectés: " + str(self.connectedplayers) + " | " + str(self.rostr));

    def winpop(self):
        popup = Tk();
        popup.wm_title("Gagné");
        label = Label(popup, text = "Partie gagnée");
        label.pack(side = "top", pady = 10);
        B1 = Button(popup, text="Ok", command = popup.destroy);
        B1.pack();
        popup.mainloop();

    def win(self):
        self.winpop();
        self.Client.TriggerServerEvent("game:win");