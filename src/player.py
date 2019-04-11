from vector import Vector2

class Player:
    def __init__(self):
        self.pos = Vector2(1, 1);
        self.life = 10;
        self.actions = 2;

        self.Client = None;
        self.freeze = True;
        self.stats = None;
        self.connectedplayers = None;

    def move(self, x, y):
        self.pos.x = x;
        self.pos.y = y;

        self.actions -= 1;

        self.Client.TriggerServerEvent("player:move", self.pos.coords());

    def setlife(self, life):
        self.life = life;
        self.stats.set("Vie: " + str(self.life) + " | Joueurs connectés: " + str(self.connectedplayers));

    def SetClient(self, cl, connecteds):
        self.Client = cl;
        self.connectedplayers = connecteds;

        self.Client.RegisterClientEvent("game:turn");
        self.Client.AddEventHandler("game:turn", self.startround);

    def AddConnected(self):
        self.connectedplayers += 1;
        self.stats.set("Vie: " + str(self.life) + " | Joueurs connectés: " + str(self.connectedplayers));

    def SetTxt(self, str):
        self.stats = str;

    def FreezePos(self, st):
        self.freeze = st;

    def startround(self, shit):
        self.freeze = False;
        #self.actions = 2;

    def finishround(self):
        self.Client.TriggerServerEvent("player:endround");
        self.freeze = True;
        self.actions = 2;