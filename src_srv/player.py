from vector import Vector2
from random import randint

class Player:
    def __init__(self):
        self.life = 10;
        self.actions = 2;

    def SetLife(self, n):
        self.life = n;

    def GetLife(self):
        return self.life;

    def SetActions(self, n):
        self.actions = n;

    def GetActions(self):
        return self.actions;

class Cow:
    def __init__(self, map):
        #self.cb = cb;

        self.x = None;
        self.y = None;
        self.pos = None;
        self.map = map;

        self.CreatePos();

        self.found = False;

    def CreatePos(self):
        self.x = randint(1, 13);
        self.y = randint(1, 13);

        if self.map[self.x][self.y] == "#":
            self.CreatePos();
        else:
            self.pos = Vector2(self.x, self.y);
            #self.cb();
