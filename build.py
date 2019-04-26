import py_compile;
import shutil;

SERVER_FILES = [
    "game",
    "map",
    "player",
    "vector",
    "msrv"
]

for i in SERVER_FILES:
    py_compile.compile("./src_srv/" + i + ".py", "./build/server/" + i + ".pyc");

CLIENT_FILES = [
    "cow",
    "helptext",
    "sound",
    "vector",
    "player",
    "nclient"
];

for i in CLIENT_FILES:
    py_compile.compile("./src/" + i + ".py", "./build/client/" + i + ".pyc");

try:
    shutil.copytree("./src/images", "./build/client/images");
except shutil.Error as e:
    print(e)
except OSError as e:
    print(e)

try:
    shutil.copytree("./src/sounds", "./build/client/sounds");
except shutil.Error as e:
    print(e)
except OSError as e:
    print(e)