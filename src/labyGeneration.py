import random

labyrinth = [['#' for i in range(15)] for i in range(15)]
nodes = 0

# Constants positions for nodes check
MOUV = [[2, 0], [-2, 0], [0, 2], [0, -2]]

def union(a, b):
    for i in range(nodes):
        if nodeID[i] == a:
            nodeID[i] = b

def find(a):
    print(a)
    return nodeID[a - 1]

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


# Node placement
for i in range(15):
    for j in range(15):
        if i % 2 == 1 and j % 2 == 1:
            labyrinth[i][j] = nodes + 1
            nodes += 1

# Find array initialisation
nodeID = [0 for i in range(nodes)]
for i in range(nodes):
    nodeID[i] = i + 1

# Arc generation
arcs = []
for i in range(15):
    for j in range(15):
        if i % 2 ==1 and j % 2 == 1:
            for k in range(4):
                nl = i + MOUV[k][0]
                nc = j + MOUV[k][1]

                if inArray(nl, nc):
                    a = Arc(labyrinth[i][j], labyrinth[nl][nc], i, j)
                    arcs.append(a)
# Shuffle Arc list
random.shuffle(arcs)

# Print Array
for i in range(15):
    for j in range(15):
        print(labyrinth[i][j], end="")
    print('\n', end="")

print(nodes)
print(nodeID)

print(len(arcs))