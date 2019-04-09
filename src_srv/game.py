class Game:
    def __init__(self, server):
        self.Server = server;

        self.playerturn = 0;

    def start(self):
        self.Server.RegisterServerEvent("player:endround");
        self.Server.AddEventHandler("player:endround", self.Next);

        self.Server.RegisterServerEvent("player:foundcow");
        self.Server.AddEventHandler("player:foundcow", self.end);

        self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");

    def Next(self, shit):
        if self.playerturn == 0:
            self.playerturn = 1;
        else:
            self.playersturn = 0;

        self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");

    def end(self):
        print("C'est fini");