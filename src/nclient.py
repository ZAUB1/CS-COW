import socket

class ClientEvent:
    def __init__(self):
        self.events = {};

    def RegisterClientEvent(self, n):
        self.events[n] = None;

    def AddEventHandler(self, n, cb):
        self.events[n] = cb;

    def TriggerInternalEvent(self, n):
        if self.events[n]:
            self.events[n]();

Client = ClientEvent();

def Main():
    #address = "game.lalife-rp.fr"
    address = "127.0.0.1";
    s = socket.socket();
    s.connect((address, 120));

    while True:
        data = s.recv(1024);
        data = data.decode("UTF-8");

        if not data:
            break;
        elif data == "connected":
            print("-> Connected to server");
        else:
            Client.TriggerInternalEvent(data);

    s.close();

def testfunc():
    print("pouet");

Client.AddEventHandler("testevent", testfunc);

if __name__ == "__main__":
    Main()