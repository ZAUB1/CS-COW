from vector import Vector2

class Player:
    def __init__(self, cl):
        self.pos = Vector2(1, 1);
        self.life = 10;

        self.Client = cl;

    def move(self, x, y):
        self.pos.x = x;
        self.pos.y = y;

        self.Client.TriggerServerEvent("player:move", self.coords);

    def setlife(self, life):
        self.life = life;

        self.Client.TriggerServerEvent("player:setlife", self.life);