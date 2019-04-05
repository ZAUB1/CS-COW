import random

labyrinth = [['#' for i in range(15)] for i in range(15)]
nodes = 0

# Constants positions for nodes check
MOUV    = [[2, 0], [-2, 0], [0, 2], [0, -2]]
MOUVARC = [[1, 0], [-1, 0], [0, 1], [0, -1]]

# Convert 2D Array in a simple string and return it
def MaptoString(array):
    str = ""
    for i in range(15):
        for j in range(15):
            str += array[i][j]
    return str

# If a and b has differents root union
def union(a, b):
    aID = find(a)
    bID = find(b)

    if aID != bID:
        nodeID[bID] = aID

# Recursive function which find parent of a node
# If the node is contained in himself it's the root, we can stop the function
# Else keep calling parent node
def find(a):
    if nodeID[a] == a:
        return a
    return find(nodeID[a])

# Check it the position isn't "out of bounds"
def inArray(line, column):
    # if 0 <= line < 15 and 0 <= column < 15 then ...
    if line >= 0 and line < 15 and column >= 0 and column < 15:
        if labyrinth[line][column] != '#':
            return True
    return False

# Arc class
class Arc:
    def __init__(self, nodeA, nodeB, line, column):
        self.column = column
        self.line   = line
        self.nodeA  = nodeA
        self.nodeB  = nodeB

# Launch generation algorithm
def genLaby():
    global labyrinth, nodeID, nodes
    # Node placement
    for i in range(15):
        for j in range(15):
            if i % 2 == 1 and j % 2 == 1:
                labyrinth[i][j] = nodes
                nodes += 1

    # Find array initialisation
    nodeID = [0 for i in range(nodes)]
    for i in range(nodes):
        nodeID[i] = i

    # Arc generation
    arcs = []
    for i in range(15):
        for j in range(15):
            if i % 2 ==1 and j % 2 == 1:
                for k in range(4):
                    nl = i + MOUV[k][0]
                    nc = j + MOUV[k][1]

                    if inArray(nl, nc):
                        a = Arc(labyrinth[i][j], labyrinth[nl][nc], i + MOUVARC[k][0], j + MOUVARC[k][1])
                        arcs.append(a)

    # Shuffle Arc list
    random.shuffle(arcs)

    # Creating arc and labyrinth
    for arc in arcs:
        if find(arc.nodeA) != find(arc.nodeB):
            union(arc.nodeA, arc.nodeB)
            labyrinth[arc.line][arc.column] = '.'

    # Clear nodes numbers in labyrinth
    for i in range(15):
        for j in range(15):
            if labyrinth[i][j] != '#' and labyrinth[i][j] != '.':
                labyrinth[i][j] = '.'

    # Spawn traps and heal randomly (p = 1/20)
    for i in range(15):
        for j in range(15):
            if labyrinth[i][j] == '.':
                r = random.randint(0, 19)
                if r == 1:
                    labyrinth[i][j] = 'H'
                elif r == 5:
                    labyrinth[i][j] = 'T'

    # No trap / heal on spawn
    labyrinth[1][1] = '.'

    return labyrinth