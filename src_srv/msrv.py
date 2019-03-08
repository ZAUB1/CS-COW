import socket
import sys
from _thread import start_new_thread
import json

HOST = '';
PORT = 120;

conn = None;

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);

class SrvEvents:
    def __init__(self):
        self.sevents = {};
        self.conns = [];
        self.lastsource = None;

    def RegisterServerEvent(self, n):
        self.sevents[n] = None;

    def TriggerIntervalEvent(self, n):
        self.sevents[n]();

    def AddEventHandler(self, n, cb):
        #if n in self.sevents == True:
        self.sevents[n] = cb;
        #else:
        #    print("-> Event doesn't exist");

    def TriggerGlobalClientEvent(self, n, *args):
        arr = [];

        for i in args:
            arr.append(i);

        for i in range(len(self.conns)):
            self.conns[i].send(bytes(json.dumps({"n": n, "args": arr}), 'utf-8'));

    def TriggerClientEvent(self, client, n, *args):
        arr = [];

        for i in args:
            arr.append(i);

        client.send(bytes(json.dumps({"n": n, "args": arr}), 'utf-8'));

    def GetLastSource(self):
        return self.lastsource;

Server = SrvEvents();

print(":: Socket Created");

s.bind((HOST, PORT));
print(":: Socket port " + str(PORT));

s.listen(0);
print(":: Listening...");

def client_thread(conn, addr):
    Server.TriggerClientEvent(conn, "connected");

    while True:
        data = conn.recv(1024);
        data = data.decode("UTF-8");

        if not data:
            break;
        else:
            Server.lastsource = conn;
            Server.TriggerIntervalEvent(data)

    Server.conns.remove(conn);
    conn.close();

    print("-> Disconnected from " + addr[0] + ":" + str(addr[1]));

def srvloop():
    while True:
        conn, addr = s.accept();
        Server.conns.append(conn);

        print("-> Connected to " + addr[0] + ":" + str(addr[1]));

        start_new_thread(client_thread, (conn, addr, ));

def OnClientConnected():
    print(Server.GetLastSource());

Server.AddEventHandler("onclientconnected", OnClientConnected);

srvloop();