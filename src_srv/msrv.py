import threading
import socket
import sys
import json
import signal
from threading import Thread
#import deamon
#from thread import start_new_thread

HOST = '';
PORT = 110;

conn = None;

class SrvEvents:
    def __init__(self):
        self.sevents = {};
        self.teststr = "zaejzej";
        self.conn = None;

    def RegisterServerEvent(self, n):
        self.sevents[n] = None;

    def TriggerIntervalEvent(self, n):
        self.sevents[n]();

    def AddEventHandler(self, n, cb):
        print("Handled", cb)
        #if self.sevents[n] != None:
        self.sevents[n] = cb;

    def TriggerGlobalClientEvent(self, n, *args):
        self.conn.sendall(b"testesteste");
        #conn.sendall(json.dumps({n: n, arg: list(args)}))

Server = SrvEvents();

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

print("Socket Created");

s.bind((HOST, PORT));
print("Socket port " + str(PORT));

s.listen(10);
print("Listening...");

Server.RegisterServerEvent("srv:onconn");

def client_thread(conn):
    Server.TriggerIntervalEvent("srv:onconn");

    print("Yup", conn);

    conn.send(b"connected");

    while True:
        data = conn.recv(1024);
        print(data);

        if not data:
            break;

        conn.sendall(b"ok");
    conn.close();

def srvloop():
    while True:
        conn, addr = s.accept();
        Server.conn = conn;
        print("Connected to " + addr[0] + ":" + str(addr[1]));

        #start_new_thread(client_thread, (conn,));
        thread = Thread(target = client_thread, args = (conn, ))
        thread.start();
        thread.join();


def testfunc():
    print("OUIIIi")
    Server.TriggerGlobalClientEvent("blblbl");

Server.AddEventHandler("srv:onconn", testfunc);

srvloop();

s.close();