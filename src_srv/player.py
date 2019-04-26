from vector import Vector2
from random import randint

class Player:
    def __init__(self):
        self.pos = Vector2(1, 1) #Création de la position du joueur

class Cow:
    def __init__(self, map): #Initialisation de la classe de la vache avec la carte du jeu en argument
        self.x = None;
        self.y = None;
        self.pos = None;
        self.map = map;

        self.CreatePos(); #On génère la position de la vache

        self.found = False;

    def CreatePos(self): #Fonction qui genère aléatoirement la position de la vache
        self.x = randint(1, 13);
        self.y = randint(1, 13);

        if self.map[self.y][self.x] == "T": #On s'assure que la vache n'apparaisse pas sur un piège
            self.CreatePos();
        else:
            self.pos = Vector2(self.x, self.y);
