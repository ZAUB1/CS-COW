import py_compile;
import shutil;
import subprocess;
import os
from platform import system;
g_system = system();

from pkgutil import iter_modules

def module_exists(module_name):
    return module_name in (name for loader, name, ispkg in iter_modules())

if (module_exists("pip") == False):
    print("[ERROR] Pip isn't installed cannot continue build");
    os._exit(1);

if module_exists("pyinstaller") == False:
    print("Installing missing package :", "pyinstaller");
    if g_system == 'Windows':
        subprocess.call(r"py -m pip install pyinstaller");
    else:
        subprocess.call(r"sudo python -m pip install pyinstaller", shell = True);

SERVER_FILES = [
    "game",
    "map",
    "player",
    "vector",
]

CLIENT_MODULES = [
    "cow",
    "player",
    "sound",
    "vector",
    "helptext",
    "discord"
]

CLIENT_LIBS = [
    "pypresence",
    "asyncio",
    "concurrent"
]

os.chdir("./src_srv");

print("Building server");

if g_system == 'Windows':
    subprocess.call(r"pyinstaller server.py --distpath ../build --workpath ../build/temp --specpath ../build/temp");
else:
    subprocess.call(r"pyinstaller server.py --distpath ../build --workpath ../build/temp --specpath ../build/temp", shell = True);

for i in SERVER_FILES:
    print("[SERVER FILES] Compiling " + i + ".py");
    py_compile.compile("./" + i + ".py", "../build/server/" + i + ".pyc");

os.chdir("../src");

print("Building client");

if g_system == 'Windows':
    subprocess.call(r"pyinstaller client.py --distpath ../build --workpath ../build/temp --specpath ../build/temp --icon=./images/favicon.ico");
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

if g_system == 'Windows':
    print("[ASSETS] Copying libs");

    try:
        shutil.copyfile("./lib/ctypes.pyd", "../build/client/ctypes.pyd");
    except shutil.Error as e:
        print(e)
    except OSError as e:
        print(e)

    try:
        shutil.copyfile("./lib/ctypes.pyd", "../build/client/_ctypes.pyd");
    except shutil.Error as e:
        print(e)
    except OSError as e:
        print(e)

    try:
        print("[ASSETS] Copying libs");
        shutil.copytree("./lib/ctypes", "../build/client/ctypes");
    except shutil.Error as e:
        print(e)
    except OSError as e:
        print(e)
else:
    try:
        print("[ASSETS] Copying libs");
        shutil.copytree("./lib/gi", "../build/client/gi");
    except shutil.Error as e:
        print(e)
    except OSError as e:
        print(e)

for i in CLIENT_LIBS:
    try:
        print("[ASSETS] Copying libs", i);
        shutil.copytree("./lib/" + i, "../build/client/" + i);
    except shutil.Error as e:
        print(e)
    except OSError as e:
        print(e)

print("Compiling contextvars");
py_compile.compile("./lib/contextvars.py", "../build/client/contextvars.pyc");

if g_system == "Windows":
    try:
        print("[ASSETS] Copying libs", "_overlapped.pyd");
        shutil.copyfile("./lib/_overlapped.pyd", "../build/client/_overlapped.pyd");
    except shutil.Error as e:
        print(e)
    except OSError as e:
        print(e)

    try:
        print("[ASSETS] Copying libs", "_contextvars.pyd");
        shutil.copyfile("./lib/_contextvars.pyd", "../build/client/_contextvars.pyd");
    except shutil.Error as e:
        print(e)
    except OSError as e:
        print(e)
else:
    try:
        print("[ASSETS] Copying libs", "_contextvars.cpython-37m-x86_64-linux-gnu.so");
        shutil.copyfile("./lib/_contextvars.cpython-37m-x86_64-linux-gnu.so", "../build/client/_contextvars.cpython-37m-x86_64-linux-gnu.so");
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
if g_system == 'Windows':
    srvlaunch = open("./server/run.cmd", 'w')
    srvlaunch.write("server.exe");
    srvlaunch.close();
else:
    srvlaunch = open("./server/run.sh", 'w')
    srvlaunch.write("sudo ./server");
    srvlaunch.close();
    subprocess.call(r"sudo chmod +x ./server/server", shell = True);
    subprocess.call(r"sudo chmod +x ./server/run.sh", shell = True);

print("Build completed successfully");