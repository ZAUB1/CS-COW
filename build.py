import py_compile;
import shutil;
import subprocess;
import os
from platform import system;
system = system();

from pkgutil import iter_modules

def module_exists(module_name):
    return module_name in (name for loader, name, ispkg in iter_modules())

if (module_exists("pip") == False):
    print("[ERROR] Pip isn't installed cannot continue build");
    os._exit(1);

if module_exists("pyinstaller") == False:
    print("Installing missing package :", "pyinstaller");
    if system == 'Windows':
        subprocess.call(r"py -m pip install pyinstaller");
    else:
        subprocess.call(r"sudo python -m pip install pyinstaller", shell = True);

SERVER_FILES = [
    "game",
    "map",
    "player",
    "vector",
    "msrv"
]

CLIENT_MODULES = [
    "cow",
    "player",
    "sound",
    "vector",
    "helptext"
]

for i in SERVER_FILES:
    print("[SERVER FILES] Compiling " + i + ".py");
    py_compile.compile("./src_srv/" + i + ".py", "./build/server/" + i + ".pyc");

os.chdir("./src");

if system == 'Windows':
    subprocess.call(r"pyinstaller client.py --distpath ../build --workpath ../build/temp --specpath ../build/temp");
else:
    subprocess.call(r"pyinstaller client.py --distpath ../build --workpath ../build/temp --specpath ../build/temp", shell = True);

try:
    print("[ASSETS] Copying images");
    shutil.copytree("./images", "../build/client/images");
except shutil.Error as e:
    print(e)
except OSError as e:
    print(e)

try:
    print("[ASSETS] Copying sounds");
    shutil.copytree("./sounds", "../build/client/sounds");
except shutil.Error as e:
    print(e)
except OSError as e:
    print(e)

for i in CLIENT_MODULES:
    print("[CLIENT MODULES] Compiling " + i + ".py");
    py_compile.compile(i + ".py", "../build/client/" + i + ".pyc");

os.chdir("../build");
print("Deleting temp files");
shutil.rmtree("./temp");

print("Creating server launcher");
if system == 'Windows':
    srvlaunch = open("./server/run.cmd", 'w')
    srvlaunch.write("py -3.7 msrv.pyc");
    srvlaunch.close();
else:
    srvlaunch = open("./server/run.sh", 'w')
    srvlaunch.write("sudo python msrv.pyc");
    srvlaunch.close();
    subprocess.call(r"sudo chmod +x ./server/run.sh");

print("Build completed successfully");