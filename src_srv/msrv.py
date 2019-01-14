import threading
import socket
import sys
from thread import start_new_thread

HOST = '';
PORT = 9999;

conn = None;

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
except socket.error, msg:
    print("Couldn't create socket. Error Code: ", str(msg[0]), "Error: ", msg[1]);
    sys.exit(0);

print("Socket Created");

try:
    s.bind((HOST, PORT));
    print("Socket port " + str(PORT));
except socket.error, msg:
    print("Bind Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]));
    sys.exit();

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

while True:
    conn, addr = s.accept();
    print("Connected to " + addr[0] + ":" + str(addr[1]));

    start_new_thread(client_thread, (conn,));

s.close();

class SrvEvents:
    def __init__(self):
        self.sevents = [];

    def strtonbr(self, str):


    def RegisterServerEvent(self, n, cb):
        return 1

    def TriggerClientEvent(self, n):
        return 1