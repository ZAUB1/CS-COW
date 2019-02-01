import socket

def Main():
    address = "127.0.0.1"
    s = socket.socket()
    s.connect((address, 110))

    while True:
        data = s.recv(1024)
        data = data.decode("UTF-8")

        print("Received", data)

    s.close()

if __name__ == "__main__":
    Main()