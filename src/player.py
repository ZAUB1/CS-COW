from vector import Vector2
from tkinter import *
from helptext import *
from sound import ThreadedSound

class Player: #Classe joueur gérant tous les differents paramètres du joueur
    def __init__(self, win):
        self.pos = Vector2(1, 1); #On initialise la position du joueur en haut de la carte
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

    def move(self, x, y): #Méthode permettant de bouger le joueur
        self.pos.x = x;
        self.pos.y = y;

        self.actions -= 1; #On enleve une action au joueur

        self.Client.TriggerServerEvent("player:move", self.pos.coords()); #On envoi les nouvelles coordonées au serveur

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

    def setlife(self, life): #Méthode permettant de changer la vie du joueur
        self.life = life;
        self.updateinfo();

    def SetClient(self, cl, connecteds, laby): #Méthode executée une fois le client connecté au serveur, permettant de recuperer la connection et le labyrinthe
        self.Client = cl;
        self.connectedplayers = connecteds;

        self.laby = laby;

        self.Client.RegisterClientEvent("game:turn");
        self.Client.AddEventHandler("game:turn", self.startround);

        self.Client.RegisterClientEvent("game:winpop");
        self.Client.AddEventHandler("game:winpop", self.winpop);

        self.Client.RegisterClientEvent("game:lost");
        self.Client.AddEventHandler("game:lost", self.losepop);

    def AddConnected(self): #Méthode permettant d'actualiser le nombre de joueurs connectés
        self.connectedplayers += 1;
        self.updateinfo();

    def SetTxt(self, str): #Méthode permettant de changer le contenu des informations principales affichées en haut à droite
        self.stats = str;

    def FreezePos(self, st): #Méthode permettant d'empecher le joueur de bouger (lorsqu'il est pris dans un piège ou que ce n'est pas son tour de jouer)
        self.freeze = st;

    def startround(self, shit): #Méthode commencant un tour
        self.freeze = False;
        self.rostr = "C'est votre tour de jouer";
        self.updateinfo();
        self.lookfortraps();

    def finishround(self): #Méthode finissant un tour
        self.Client.TriggerServerEvent("player:endround");
        self.freeze = True;
        self.actions = 2;
        self.rostr = "C'est au tour de l'autre joueur";
        self.updateinfo();

    def updateinfo(self): #Méthode métant à jour les informations principales en haut à droite
        self.stats.set("Vie: " + str(self.life) + " | Joueurs connectés: " + str(self.connectedplayers) + " | " + str(self.rostr));

    def pop(self, stri, strt): #Méthode permettant d'afficher un popup au joueur
        popup = Tk();
        popup.wm_title(strt);
        label = Label(popup, text = stri);
        label.pack(side = "top", pady = 10);
        B1 = Button(popup, text="Ok", command = popup.destroy);
        B1.pack();
        popup.mainloop();

    def winpop(self, *args): #Méthode utilisée lorsque la partie est gagnée
        self.FreezePos(True);
        ThreadedSound("./sounds/victory.mp3"); #On émet un son de victoire
        self.pop("Partie gagnée", "Gagné"); #On crée un popup de victoire

    def losepop(self, *args): #Méthode utilisée lorsque la partie est perdue
        self.FreezePos(True);
        ThreadedSound("./sounds/defeat.mp3");
        self.pop("Partie perdu (temps écoulé)", "Perdu");

    def win(self):
        self.winpop();
        self.Client.TriggerServerEvent("game:win");