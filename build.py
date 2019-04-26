import py_compile;

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