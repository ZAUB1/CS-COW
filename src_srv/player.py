from vector import Vector2
from random import randint

class Player:
    def __init__(self):
        self.pos = Vector2(1, 1)

class Cow:
    def __init__(self, map):
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
        elif self.map[self.x][self.y] == "T":
            self.CreatePos();
        else:
            self.pos = Vector2(self.x, self.y);
