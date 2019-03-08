import socket
import json

class ClientEvent:
    def __init__(self):
        self.events = {};
        self.connection = None;

    def RegisterClientEvent(self, n):
        self.events[n] = None;

    def AddEventHandler(self, n, cb):
        self.events[n] = cb;

    def TriggerInternalEvent(self, n, args):
        #if n in self.events == True:
        self.events[n](args);
        #else:
            #print("-> Event (" + n + ") doesn't exist");

    def TriggerServerEvent(self, n, *args):
        self.connection.send(bytes(n, 'utf-8'));

Client = ClientEvent();

def Main():
    address = "127.0.0.1";

    s = socket.socket();
    Client.connection = s;
    s.connect((address, 120));

    while True:
        data = s.recv(1024);
        data = data.decode("UTF-8");
        data = json.loads(data);

        if not data:
            break;
        else:
            Client.TriggerInternalEvent(data['n'], data['args']);

    s.close();

def OnConnected(args):
    print("-> Connected to server");
    Client.TriggerServerEvent("onclientconnected");

Client.RegisterClientEvent("connected");
Client.AddEventHandler("connected", OnConnected);

if __name__ == "__main__":
    Main()