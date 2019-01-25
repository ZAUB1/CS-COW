import threading
import socket
import sys
import json
#from thread import start_new_thread

print("oui")

HOST = '';
PORT = 9999;

conn = None;

class SrvEvents:
    def __init__(self):
        self.sevents = {};

    def RegisterServerEvent(self, n, cb):
        self.sevents[n] = cb;

    def TriggerIntervalEvent(self, n):
        self.sevents[n]();

    def TriggerGlobalClientEvent(self, n, *args):
        conn.send(json.dumps({n: n, arg: list(args)}))

Server = SrvEvents();

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

print("Socket Created");

s.bind((HOST, PORT));
print("Socket port " + str(PORT));
    
s.listen(10);
print("Listening...");

def client_thread(conn):
    print("Yup", conn);

    conn.send("WOW C'EST CONNECTE EN TABARNAKKKKK.\n");

    while True:
        data = conn.recv(1024);
        print(data);

        if not data:
            break;

        conn.sendall("ok");
    conn.close();

def srvloop():
	while True:
	    conn, addr = s.accept();
	    print("Connected to " + addr[0] + ":" + str(addr[1]));

	    #start_new_thread(client_thread, (conn,));

mt = threading.Thread(target = srvloop);
mt.setDaemon(true);
mt.start();

s.close();