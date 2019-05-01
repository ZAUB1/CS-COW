import random

labyrinth = [['#' for i in range(15)] for i in range(15)]
nodes = 0

# Positions constantes pour verifier si un noeud existe, tout les noeuds sont separe par une case
# "pleine". L'arc est doit etre en deux noeuds et est situe entre deux noeuds d'ou une verification
# de la case adjascente.
MOUV    = [[2, 0], [-2, 0], [0, 2], [0, -2]]
MOUVARC = [[1, 0], [-1, 0], [0, 1], [0, -1]]

# Fonction convertissant une tableau en 2D en une chaine de characteres et la retourne
def MaptoString(array):
    str = ""
    for i in range(15):
        for j in range(15):
            str += array[i][j]
    return str

# Si A et B ont sont sur une branche differente de l'arbre, alors ont unis ces branches
def union(a, b):
    aID = find(a)
    bID = find(b)

    if aID != bID:
        nodeID[bID] = aID

# Fonction qui verifie si le noeud est contenue dans lui meme (cet a dire qu'il est a la racine de
# d'une branche. Si ce n'est pas le cas la fonction se rappel recursivement avec pour parametre le
# noeud parent du noeud pour lequel elle a ete appelee initialement
def find(a):
    if nodeID[a] == a:
        return a
    return find(nodeID[a])

# Verifie si la case que l'on souhaite acceder se trouve dans le tableau, permet d'eviter des acces
# hors du tableau.
def inArray(line, column):
    # if 0 <= line < 15 and 0 <= column < 15 then ...
    if line >= 0 and line < 15 and column >= 0 and column < 15:
        if labyrinth[line][column] != '#':
            return True
    return False

# Objet representant un arc du graphe : contient simplement 4 variables
# l'emplacement de l'arc dans le labyrinthe (line, column)
# et les noeuds que l'arc relie entre eux (nodeA, nodeB)
class Arc:
    def __init__(self, nodeA, nodeB, line, column):
        self.column = column
        self.line   = line
        self.nodeA  = nodeA
        self.nodeB  = nodeB

# Fonction principale de la generation du labyrinthe, est appele a chaques nouvelle partie
def genLaby():
    global labyrinth, nodeID, nodes
    # Place les noeuds dans le labyrinthe tous a 1 case les uns des autres
    for i in range(15):
        for j in range(15):
            if i % 2 == 1 and j % 2 == 1:
                labyrinth[i][j] = nodes
                nodes += 1

    # Initialisation du tableau representant l'arbre
    nodeID = [0 for i in range(nodes)]
    for i in range(nodes):
        nodeID[i] = i

    # Genere tout les arcs possibles en verifiant depuis chaques noeuds si il y'a un autre noeud
    # accessible depuis celui-ci. Si oui on cree un arc et on le stock dans un tableau
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

    # Fonction python pour melanger le tableau contenant les arcs
    random.shuffle(arcs)

    # Boucle principale de l'union-find. Pour chaques arcs, si ces arcs relient des noeuds qui ne sont
    # pas dans une meme branche, alors on fusionne ces deux branches en appelant la fonction union()
    # On place un '.' dans le labyrinthe puisque deux noeuds sont relies
    for arc in arcs:
        if find(arc.nodeA) != find(arc.nodeB):
            union(arc.nodeA, arc.nodeB)
            labyrinth[arc.line][arc.column] = '.'

    # On nettoie le labyrinthe
    for i in range(15):
        for j in range(15):
            if labyrinth[i][j] != '#' and labyrinth[i][j] != '.':
                labyrinth[i][j] = '.'

    # Pour chaques case du labyrinthe, une probabilitee de 1/20 de creer un piege (T) et un soin (H)
    for i in range(15):
        for j in range(15):
            if labyrinth[i][j] == '.':
                r = random.randint(0, 19)
                if r == 1:
                    labyrinth[i][j] = 'H'
                elif r == 5:
                    labyrinth[i][j] = 'T'

    # Le poit d'apparition du joueur doit pas avoir de piege
    labyrinth[1][1] = '.'

    return labyrinth
