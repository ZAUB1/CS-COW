import asyncio

class Game:
    def __init__(self, server):
        self.Server = server;

        self.playerturn = 0;

    async def turn(self):
        await asyncio.sleep(0.05);
        self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");

    def start(self):
        self.Server.RegisterServerEvent("player:endround");
        self.Server.AddEventHandler("player:endround", self.Next);

        asyncio.run(self.turn());

    def Next(self, shit):
        if self.playerturn == 0:
            self.playerturn = 1;
        else:
            self.playerturn = 0;

        #self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");
        asyncio.run(self.turn());