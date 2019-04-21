import asyncio
import threading
from _thread import start_new_thread

class Game:
    def __init__(self, server):
        self.Server = server;

        self.playerturn = 0;
        self.currenttime = 300;

    def setInterval(self, func, time):
        self.e = threading.Event();
        while not self.e.wait(time):
            func();

    async def turn(self):
        await asyncio.sleep(0.05);
        self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");

    def lose(self):
        self.Server.TriggerGlobalClientEvent("game:lost");

    def countdown(self):
        if self.currenttime > 0:
            self.currenttime -= 1;
        elif self.currenttime == 0:
            self.lose();
            self.e.wait(9999999);

        self.Server.TriggerGlobalClientEvent("game:time", self.currenttime);

    def start(self):
        self.Server.RegisterServerEvent("player:endround");
        self.Server.AddEventHandler("player:endround", self.Next);

        asyncio.run(self.turn());

        start_new_thread(self.setInterval, (self.countdown, 1, ));

    def Next(self, shit):
        if self.playerturn == 0:
            self.playerturn = 1;
        else:
            self.playerturn = 0;

        #self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");
        asyncio.run(self.turn());