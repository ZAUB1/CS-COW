from vector import Vector2
from tkinter import *
from helptext import *
from sound import ThreadedSound

class Player:
    def __init__(self, win):
        self.pos = Vector2(1, 1);
        self.life = 10;
        self.actions = 2;

        self.Client = None;
        self.freeze = True;
        self.stats = None;
        self.connectedplayers = None;
        self.laby = None;

        self.nexttotrap = False;

        self.rostr = "C'est au tour de l'autre joueur";
        self.traptext = HelpText(win, "Appuyez sur E pour attaquer le piege", True, True);

    def move(self, x, y):
        self.pos.x = x;
        self.pos.y = y;

        self.actions -= 1;

        self.Client.TriggerServerEvent("player:move", self.pos.coords());

    def lookfortraps(self):
        foundt = False;

        px = self.pos.x;
        py = self.pos.y;

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

            if self.laby[cy][cx] == 'T':
                foundt = True;
                break;

        if foundt == True:
            self.nexttotrap = True;
            self.traptext.show();
        else:
            self.nexttotrap = False;
            self.traptext.hide();

    def setlife(self, life):
        self.life = life;
        self.updateinfo();

    def SetClient(self, cl, connecteds, laby):
        self.Client = cl;
        self.connectedplayers = connecteds;

        self.laby = laby;

        self.Client.RegisterClientEvent("game:turn");
        self.Client.AddEventHandler("game:turn", self.startround);

        self.Client.RegisterClientEvent("game:winpop");
        self.Client.AddEventHandler("game:winpop", self.winpop);

        self.Client.RegisterClientEvent("game:lost");
        self.Client.AddEventHandler("game:lost", self.losepop);

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
        self.lookfortraps();

    def finishround(self):
        self.Client.TriggerServerEvent("player:endround");
        self.freeze = True;
        self.actions = 2;
        self.rostr = "C'est au tour de l'autre joueur";
        self.updateinfo();

    def updateinfo(self):
        self.stats.set("Vie: " + str(self.life) + " | Joueurs connectés: " + str(self.connectedplayers) + " | " + str(self.rostr));

    def pop(self, stri, strt):
        popup = Tk();
        popup.wm_title(strt);
        label = Label(popup, text = stri);
        label.pack(side = "top", pady = 10);
        B1 = Button(popup, text="Ok", command = popup.destroy);
        B1.pack();
        popup.mainloop();

    def winpop(self, *args):
        ThreadedSound("./sounds/victory.mp3");
        self.pop("Partie gagnée", "Gagné");

    def losepop(self, *args):
        self.FreezePos(True);
        ThreadedSound("./sounds/defeat.mp3");
        self.pop("Partie perdu (temps écoulé)", "Perdu");

    def win(self):
        self.winpop();
        self.Client.TriggerServerEvent("game:win");