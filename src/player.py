from vector import Vector2

class Player:
    def __init__(self):
        self.pos = Vector2(1, 1);
        self.life = 10;

        self.Client = None;
        self.freeze = True;

    def move(self, x, y):
        self.pos.x = x;
        self.pos.y = y;

        self.Client.TriggerServerEvent("player:move", self.pos.coords());

    def setlife(self, life):
        self.life = life;

        self.Client.TriggerServerEvent("player:setlife", self.life);

    def SetClient(self, cl):
        self.Client = cl

    def FreezePos(self, st):
        self.freeze = st;