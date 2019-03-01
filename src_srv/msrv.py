import socket
import sys
from _thread import start_new_thread

HOST = '';
PORT = 120;

conn = None;

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);

class SrvEvents:
    def __init__(self):
        self.sevents = {};
        self.conns = [];

    def RegisterServerEvent(self, n):
        self.sevents[n] = None;

    def TriggerIntervalEvent(self, n):
        self.sevents[n]();

    def AddEventHandler(self, n, cb):
        print("Handled", cb)
        #if self.sevents[n] != None:
        self.sevents[n] = cb;

    def TriggerGlobalClientEvent(self, n, *args):
        for i in range(len(self.conns)):
            #self.conns[i].send(b"zboub");
            self.conns[i].send(bytes(n, 'utf-8'));

    def TriggerClientEvent(self, client, n, *args):
        client.send(bytes(n, 'utf-8'));

Server = SrvEvents();

print(":: Socket Created");

s.bind((HOST, PORT));
print(":: Socket port " + str(PORT));

s.listen(0);
print(":: Listening...");

def client_thread(conn, addr):
    conn.send(b"connected");

    Server.TriggerClientEvent(conn, "testevent");

    while True:
        data = conn.recv(1024);

        if not data:
            break;

    Server.conns.remove(conn);
    conn.close();

    print("-> Disconnected from " + addr[0] + ":" + str(addr[1]));

def srvloop():
    while True:
        conn, addr = s.accept();
        Server.conns.append(conn);

        print("-> Connected to " + addr[0] + ":" + str(addr[1]));

        start_new_thread(client_thread, (conn, addr, ));

srvloop();