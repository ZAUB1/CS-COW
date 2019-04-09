import socket
import sys
from _thread import start_new_thread
import json
import os

from map import *
from player import *
from game import *

HOST = "";
PORT = 120;

conn = None;
players = {};

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);

map = genLaby();
cow = Cow(map);

class SrvEvents:
    def __init__(self):
        self.sevents = {};
        self.conns = [];
        self.connsbyid = {};
        self.lastsource = None;
        self.lastid = None;

    def RegisterServerEvent(self, n):
        self.sevents[n] = None;

    def TriggerIntervalEvent(self, n, args):
        self.sevents[n](args);

    def AddEventHandler(self, n, cb):
        self.sevents[n] = cb;

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

    def SendAllExcept(self, n, client, *args):
        arr = [];

        for i in args:
            arr.append(i);

        for i in range(len(self.conns)):
            if (self.conns[i].getpeername()[1] != client) == True:
                self.conns[i].send(bytes(json.dumps({"n": n, "args": arr}), 'utf-8'));

    def GetLastSource(self):
        return self.lastsource;

    def GetLastId(self):
        return self.lastid;

Server = SrvEvents();

game = Game(Server);

print(":: Socket Created");

s.bind((HOST, PORT));
print(":: Socket port " + str(PORT));

s.listen(0);
print(":: Listening...");

def prompt():
    while True:
        line = sys.stdin.readline()

        if "clist" in line:
            for i in range(len(Server.conns)):
                print(i + 1, "- id:", str(Server.conns[i].getpeername()[1]) + ",", "ip:", Server.conns[i].getpeername()[0]);
        elif "exit" in line:
            os._exit(1)

start_new_thread(prompt, ());

def client_thread(conn, addr):
    Server.TriggerClientEvent(conn, "connected");

    if len(Server.conns) > 1:
        game.start();

    while True:
        data = conn.recv(1024);
        data = data.decode("UTF-8");

        if not data:
            break;
        else:
            data = json.loads(data);
            Server.lastsource = conn;
            Server.lastid = conn.getpeername()[1];

            Server.TriggerIntervalEvent(data['n'], data['args']);

    Server.conns.remove(conn);
    conn.close();

    print("-> Disconnected from " + addr[0] + ":" + str(addr[1]));

def srvloop():
    while True:
        conn, addr = s.accept();
        Server.conns.append(conn);

        print("-> Connected to " + addr[0] + ":" + str(addr[1]));

        start_new_thread(client_thread, (conn, addr, ));

def OnClientConnected(args):
    players[Server.GetLastId()] = Player();

    Server.TriggerClientEvent(Server.GetLastSource(), "firstdata", MaptoString(map), cow.pos.coords());

Server.AddEventHandler("onclientconnected", OnClientConnected);

#Player events

def moveply(args):
    players[Server.GetLastId()].pos.Set(args[0][0], args[0][1]);
    Server.SendAllExcept("oplayer:newpos", Server.GetLastId(), players[Server.GetLastId()].pos.coords());

Server.AddEventHandler("player:move", moveply);

def changelife(args):
    players[Server.GetLastId()].SetLife(args[0]);

Server.AddEventHandler("player:setlife", changelife);

srvloop();