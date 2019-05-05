from pypresence import Presence
from _thread import start_new_thread
import threading

client_id = "574530833927503894";

class DPresence:
    def __init__(self):
        self.RPC = Presence(client_id = client_id);
        try:
            self.RPC.connect();
            self.updatepresence();
            start_new_thread(self.setInterval, (self.updatepresence, 15));
        except:
            print("[WARNING] Discord not connected");

    def setInterval(self, func, time): #Méthode permettant d'executer toutes les n secondes une autre fonction
        self.e = threading.Event();
        while not self.e.wait(time):
            func();

    def updatepresence(self):
        self.RPC.update(large_image = "cow_full");
