import socket
import json

from cow import *

map = None;
cow = None;

class ClientEvent:
    def __init__(self):
        self.events = {};
        self.connection = None;

    def RegisterClientEvent(self, n):
        self.events[n] = None;

    def AddEventHandler(self, n, cb):
        self.events[n] = cb;

    def TriggerInternalEvent(self, n, args):
        self.events[n](args);

    def TriggerServerEvent(self, n, *args):
        arr = [];

        for i in args:
            arr.append(i);

        self.connection.send(bytes(json.dumps({"n": n, "args": arr}), 'utf-8'));

Client = ClientEvent();

def Main():
    address = "127.0.0.1";

    s = socket.socket();
    Client.connection = s;
    s.connect((address, 120));

    while True:
        data = s.recv(1024);
        data = data.decode("UTF-8");

        if not data:
            break;
        else:
            data = json.loads(data);
            Client.TriggerInternalEvent(data['n'], data['args']);

    s.close();

def OnConnected(args):
    print("-> Connected to server");
    Client.TriggerServerEvent("onclientconnected");

Client.RegisterClientEvent("connected");
Client.AddEventHandler("connected", OnConnected);

def initd(args):
    global map;
    global cow;

    map = args[0];
    cow = Cow(args[1][0], args[1][1]);

Client.RegisterClientEvent("firstdata");
Client.AddEventHandler("firstdata", initd);

if __name__ == "__main__":
    Main();