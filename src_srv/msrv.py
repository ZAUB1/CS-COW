import socket
import sys
from _thread import start_new_thread
import threading
import json
import os
import asyncio

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

def setInterval(func, time):
    e = threading.Event();
    while not e.wait(time):
        func();

class QItem:
    def __init__(self, client, stri):
        self.client = client;
        self.stri = stri;

class SrvEvents:
    def __init__(self):
        self.sevents = {};
        self.conns = [];
        self.connsbyid = {};
        self.lastsource = None;
        self.lastid = None;
        self.queued = [];

        start_new_thread(self.startsendloop, ());

    def sendloop(self):
        if len(self.queued) > 0:
            print(self.queued[0].stri);
            self.queued[0].client.send(bytes(self.queued[0].stri, "utf-8"));
            del self.queued[0];

    def startsendloop(self):
        setInterval(self.sendloop, 0.2);

    def addtosend(self, client, stri):
        self.queued.append(QItem(client, stri));

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
            self.addtosend(self.conns[i], json.dumps({"n": n, "args": arr}));

    def TriggerClientEvent(self, client, n, *args):
        arr = [];

        for i in args:
            arr.append(i);

        self.addtosend(client, json.dumps({"n": n, "args": arr}));

    def SendAllExcept(self, n, client, *args):
        arr = [];

        for i in args:
            arr.append(i);

        for i in range(len(self.conns)):
            if (self.conns[i].getpeername()[1] != client) == True:
                self.addtosend(self.conns[i], json.dumps({"n": n, "args": arr}));

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
        Server.SendAllExcept("oplayer:connected", conn.getpeername()[1]);
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

async def OnClientConnected(args):
    players[Server.GetLastId()] = Player();

    await asyncio.sleep(0.5);
    Server.TriggerClientEvent(Server.GetLastSource(), "firstdata", MaptoString(map), cow.pos.coords(), len(Server.conns));

def handleconnection(args):
    asyncio.run(OnClientConnected(args));

Server.AddEventHandler("onclientconnected", handleconnection);

#Player events

async def sendnewpos():
    await asyncio.sleep(0.05);
    Server.SendAllExcept("oplayer:newpos", Server.GetLastId(), players[Server.GetLastId()].pos.coords());

def moveply(args):
    players[Server.GetLastId()].pos.Set(args[0][0], args[0][1]);
    #Server.SendAllExcept("oplayer:newpos", Server.GetLastId(), players[Server.GetLastId()].pos.coords());
    asyncio.run(sendnewpos());

Server.AddEventHandler("player:move", moveply);

def wingame(args):
    Server.TriggerGlobalClientEvent("players:reveal");
    Server.SendAllExcept("game:winpop", Server.GetLastId());

Server.RegisterServerEvent("game:win");
Server.AddEventHandler("game:win", wingame);

srvloop();