import asyncio
import threading
from _thread import start_new_thread

def setInterval(func,time):
    e = threading.Event();
    while not e.wait(time):
        func();

class Game:
    def __init__(self, server):
        self.Server = server;

        self.playerturn = 0;
        self.currenttime = 300;

    async def turn(self):
        await asyncio.sleep(0.05);
        self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");

    def countdown(self):
        self.currenttime -= 1;
        self.Server.TriggerGlobalClientEvent("game:time", self.currenttime);

    def start(self):
        self.Server.RegisterServerEvent("player:endround");
        self.Server.AddEventHandler("player:endround", self.Next);

        asyncio.run(self.turn());

        start_new_thread(setInterval, (self.countdown, 1, ));

    def Next(self, shit):
        if self.playerturn == 0:
            self.playerturn = 1;
        else:
            self.playerturn = 0;

        #self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");
        asyncio.run(self.turn());