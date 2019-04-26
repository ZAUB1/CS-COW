import asyncio
import threading
from _thread import start_new_thread

class Game: #Classe gérant la partie en cours
    def __init__(self, server):
        self.Server = server; #On récupère la classe Server afin de pouvoir interagir avec les clients

        self.playerturn = 0;
        self.currenttime = 300; #On initialise un temps de jeu

    def setInterval(self, func, time): #Méthode permettant d'executer toutes les n secondes une autre fonction
        self.e = threading.Event();
        while not self.e.wait(time):
            func();

    async def turn(self): #Méthode asynchrone "passant le tour" à l'autre joueur
        await asyncio.sleep(0.1);
        self.Server.TriggerClientEvent(self.Server.conns[self.playerturn], "game:turn");

    def lose(self): #Méthode executée lorsque la partie est perdue
        self.Server.TriggerGlobalClientEvent("game:lost");

    def countdown(self): #Méthode executée toutes les secondes gérant le temps de jeu restant
        if self.currenttime > 0:
            self.currenttime -= 1;
        elif self.currenttime == 0:
            self.lose();
            self.e.wait(9999999);

        self.Server.TriggerGlobalClientEvent("game:time", self.currenttime); #On envoi le temps de jeu aux clients

    async def sendstart(self):
        await asyncio.sleep(0.5);
        self.Server.TriggerGlobalClientEvent("game:started"); #On envoi aux clients que la partie est commencée

    def start(self): #Méthode permettant de commencer la partie
        self.Server.RegisterServerEvent("player:endround");
        self.Server.AddEventHandler("player:endround", self.Next);

        asyncio.run(self.turn());

        start_new_thread(self.setInterval, (self.countdown, 1, )); #On execute la gestion du temps de manière asynchrone pour ne pas bloquer le reste du programme

        asyncio.run(self.sendstart());

    def Next(self, shit): #On passe le tour
        if self.playerturn == 0:
            self.playerturn = 1;
        else:
            self.playerturn = 0;

        asyncio.run(self.turn());