import Vector2 from vector
from random import randint

class Player:
    def __init__(self):
        self.life = 10;
        self.actions = 2;

    def SetLife(self, n):
        self.life = n;

    def GetLife(self)
        return self.life;

    def SetActions(self, n):
        self.actions = n;

    def GetActions(self):
        return self.actions;

class Cow:
    def __init__(self, map):
        x = randint(1, 13);
        y = randint(1, 13);

        self.pos = Vector2(x, y);
        self.found = False;
