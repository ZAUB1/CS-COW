import socket

def Main():
    print("Send 'q' to exit\n")
    address = "127.0.0.1"
    nick = raw_input("nick: ")

    s = socket.socket()
    s.connect((address, 9999))

    s.send("WASSUP AVEC LES BISCUITS");

    while True:
        data = s.recv(1024)
        data = data.decode("UTF-8")

        print(data)

    s.close()

if __name__ == "__main__":
    Main()