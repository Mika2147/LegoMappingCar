import time

CAR = 1
WALL = 2
EMPTY = 3
TARGET = 4
STRAIGHT = 1
LEFT = 2
RIGHT = 3
BACKWARDS = 4

MAZE = [
    [WALL, WALL, WALL, WALL, WALL, WALL],
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL, WALL, WALL, WALL, EMPTY, WALL],
    [WALL, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
    [WALL, EMPTY, WALL, WALL, EMPTY, WALL],
    [WALL, CAR, WALL, EMPTY, EMPTY, WALL],
    [WALL, WALL, WALL, WALL, WALL, WALL],
]

FOUND = False


def printMaze():
    print("+-------------+")
    for line in MAZE:
        print("| ", end="")
        for elem in line:
            if elem == WALL:
                print("+", end=" ")
            elif elem == EMPTY:
                print(" ", end=" ")
            elif elem == CAR:
                print("o", end=" ")

        print("|")
    print("+-------------+\n")


def findCarPosition(maze):
    for index_line, line in enumerate(maze):
        for index_elem, elem in enumerate(line):
            if elem == CAR:
                return (index_line, index_elem)


def getNewMovement():
    # TODO Get Data from the Service
    return STRAIGHT


def updateMaze():
    if getNewMovement() == STRAIGHT:
        x, y = findCarPosition(MAZE)
        if MAZE[x-1][y] == EMPTY:
            MAZE[x][y] = EMPTY
            MAZE[x-1][y] = CAR
        elif MAZE[x-1][y] == TARGET:
            FOUND = True
            print("Found the Target!")
            exit()
        else:
            print("Render issues, Car is going to drive in the Wall..")
            exit()


def wait():
    time.sleep(2)


while not FOUND:
    printMaze()
    updateMaze()
    wait()


'''

+-------------+
| + + + + + + |
| +         + |
| + + + +   + |
| +         + |
| +   + +   + |
| + o +     + |
| + + + + + + |
+-------------+

+-------------+
| + + + + + + |
| +         + |
| + + + +   + |
| +         + |
| + o + +   + |
| +   +     + |
| + + + + + + |
+-------------+

+-------------+
| + + + + + + |
| +         + |
| + + + +   + |
| + o       + |
| +   + +   + |
| +   +     + |
| + + + + + + |
+-------------+

Render issues, Car is going to drive in the Wall..

'''
