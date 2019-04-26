#  CS COW (Capture the Sneaky Cow)
## What's this ?
CS COW is a standalone game made with python. It's actually multiplayer that's why the git is spared in two different folders (server and clients).
## Who ?
* ZAUB1: Main runtime, server / client communication and game mechanics
* Volham: Random map generation (./src_srv/map.py)
* Aerhino: Rendering from map string using Tkinter
## How to run ?
Here are the basics commands to run the thing (:warning: Requires node and npm to run this way)

|                |Command                        |What for ?                   |
|----------------|-------------------------------|-----------------------------|
|Start server    |`npm run server`         	 |Starts the server and listens for clients.            |
|Start client    |`npm run client`               |Starts a client|