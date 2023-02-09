from mindstorms import (
    MSHub,
    Motor,
    MotorPair,
    ColorSensor,
)
from mindstorms.operator import not_equal_to
import time
"""
should_morse = True
try:
    b_empty = ColorSensor("E") # b o
    d_next = ColorSensor("C")# d //
    f_id = ColorSensor("D")    # f _
except:
    should_morse = False

SHORT = "."
LONG = "-"
EMPTY = "/"
BLANK = " "
NIL = ""
# WHITESPACE = "//"
WHITESPACE = EMPTY
def generate_morse_codes():
    morse_codes = {}
    morse_codes["0"] = LONG
    morse_codes["1"] = SHORT

    morse_codes["-"] = SHORT + SHORT
    morse_codes["2"] = SHORT + LONG

    morse_codes["3"] = SHORT + SHORT + SHORT
    morse_codes["4"] = SHORT + SHORT + LONG

    morse_codes["5"] = SHORT + LONG + SHORT
    morse_codes["6"] = SHORT + LONG + LONG

    morse_codes["5"] = LONG + SHORT + SHORT
    morse_codes["6"] = LONG + SHORT + LONG

    morse_codes["7"] = LONG + LONG + SHORT
    morse_codes["8"] = LONG + LONG + LONG

    morse_codes["9"] = SHORT + SHORT + SHORT + SHORT

    morse_codes["E"] = SHORT * 5 + (BLANK + SHORT) * 3

    return morse_codes


CODE = generate_morse_codes()
"""
MAX_TURN_ROTAIONS = 0.5
MIN_TURN_ROTATIONS = 0.05
ABSOLUTE_MIN_TURN_ROTATIONS = 0.01

MAX_TURN_SPEED = 50
MIN_TURN_SPEED = 5

CORRECTION_SPEED = 1
CORRECTION_ROTATIONS = 0.01

MAX_SPEED_CM_MOVE = 8

ROTATION_ACCURACY = 10
CORRECTION_ACCURACY = 0

# Knoten
# (id, Kante1, Kante2, Kante3, Kante 4)
# Kante
# (Richtung x, Richtung y, Zielknoten, Entfernung)
# -1 means unknown
# -2 means no destiantion
#nodes = {0: [0, [1, 0, 1, 48.5], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 1: [1, [1, 0, -1, -1], [0, 1, 2, 112.0], [-1, 0, 0, 48.5], [0, -1, -1, -1]], 2: [2, [1, 0, 4, 48.0], [0, 1, -1, -1], [-1, 0, 3, 67.0], [0, -1, 1, 112.0]], 3: [3, [1, 0, 2, 67.0], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 4: [4, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, 2, 48.0], [0, -1, 5, 132.5]], 5: [5, [1, 0, -1, -1], [0, 1, 4, 132.5], [-1, 0, -1, -1], [0, -1, -1, -1]]}
#nodes = {0: [0, [1,0,1,79.5],[0,1,-1,-1],[-1,0,-1,-1],[0,-1,-1,-1]], 1: [1, [1,0,-1,-1],[0,1,2,110.5],[-1,0,0,79.5],[0,-1,-1,-1]], 2: [2, [1,0,4,55.0],[0,1,-1,-1],[-1,0,3,58.5],[0,-1,1,110.5]], 3: [3, [1,0,2,58.5],[0,1,-1,-1],[-1,0,-1,-1],[0,-1,-1,-1]], 4: [4, [1,0,-1,-1],[0,1,-1,-1],[-1,0,2,55.0],[0,-1,5,119.0]], 5: [5, [1,0,-1,-1],[0,1,4,119.0],[-1,0,-1,-1],[0,-1,-1,-1]]}
nodes = open("data.json", "r").read()
distance = {}
predecesour = {}
# defines the direction the vehicle is moving in the map
currentDirection = [1, 0]
currentDistanceFromLastNode = 0
currentNode = 0
currentDestination = 1
lastDestination = 0
searching = True

hub = MSHub()

motorLeft = Motor("A")
motorRight = Motor("B")
motors = MotorPair("A", "B")
motors.set_motor_rotation((-9 * 2) , 'cm')

currentRotation = 0
plannedRotation = 0

colorSensor = ColorSensor('F')
"""
def display_morse(morse_code, wait=True):
    character = []
    import time
    for character in morse_code.strip():
        if character == BLANK:
            hub.light_matrix.write("o")
        elif character == SHORT:
            hub.light_matrix.write("S")
        elif character == LONG:
            hub.light_matrix.write("L")
        else:
            hub.light_matrix.write(character)
        if wait:
            hub.right_button.wait_until_pressed()
        time.sleep(1)
        hub.light_matrix.write("")
        time.sleep(1)
    hub.speaker.beep()

def de_morse(morse_code):
    def compare(word):
        return list(CODE.keys())[list(CODE.values()).index(word)]

    data = NIL
    res = []
    for element in morse_code.split(EMPTY):
        element = element.strip()
        if BLANK in element:
            for word in element.split(BLANK):
                data += str(compare(word))
            data += BLANK
        else:
            if len(element) >= 1:
                data += str(compare(element)) + BLANK
    shorten = False
    for element in data.strip().split(BLANK):
        if len(data.strip().split(BLANK)) == 2:
            res.append((element))
            shorten = True
        else:
            res.append((element))
            shorten = False

    if shorten:
        res.append(-1)
        res.append(-1)
    print("de_morse() res=", res)
    return res


def receive():
    node, node_id = {}, 0
    node[node_id] = [node_id]
    collecting = True
    morsed_value = NIL
    waiting_counter = 0
    while collecting:
        if hub.right_button.is_pressed():
            morsed_value += SHORT
            time.sleep(1)
            display_morse("S", False)
            waiting_counter = 0
        elif hub.left_button.is_pressed():
            morsed_value += LONG
            time.sleep(1)
            display_morse("L", False)
            waiting_counter = 0
        elif not_equal_to(b_empty.get_color(), None):
            morsed_value += BLANK
            time.sleep(1)
            display_morse("_", False)
            waiting_counter = 0
        elif not_equal_to(d_next.get_color(), None):
            morsed_value += WHITESPACE
            time.sleep(1)
            display_morse("/", False)
            waiting_counter = 0
        elif not_equal_to(f_id.get_color(), None):
            waiting_counter += 1
            if len(morsed_value) > 1:
                tmp = de_morse(morsed_value)
                morsed_value = NIL
                node[node_id].append(tmp)
                print(tmp, node)
        else:
            waiting_counter += 1
            print(morsed_value, node, waiting_counter)
            hub.speaker.beep()
            if len(node[node_id]) == 2:
                node_id += 1
                node[node_id] = [node_id]
            if waiting_counter == 100:
                waiting_counter = 0
                collecting = False
                display_morse("F")
"""
def compareArrays(first, second) -> bool:
    if len(first) != len(second):
        return False

    for i in range(0, len(first)):
        if first[i] != second[i]:
            return False

    return True

def directionPosition(directionX, directionY):
    ret = -1
    if directionX == 1:
        ret = 1
    elif directionX == -1:
        ret = 3
    elif directionY == 1:
        ret = 2
    elif directionY == -1:
        ret = 4
    return ret

def getAbsoluteDirection(leftOrRight):
    res = [0, 0]
    global currentDirection
    print("current direction:" + str(currentDirection) + " leftorright:" + str(leftOrRight))
    if compareArrays(currentDirection, [1, 0]):
        if leftOrRight == -1:
            res = [0, -1]
        elif leftOrRight == 0:
            res = [-1, 0]
        elif leftOrRight == 1:
            res = [0, 1]
    elif compareArrays(currentDirection,[0, 1]):
        if leftOrRight == -1:
            res = [1, 0]
        elif leftOrRight == 0:
            res = [0, -1]
        elif leftOrRight == 1:
            res = [-1, 0]
    elif compareArrays(currentDirection, [-1, 0]):
        if leftOrRight == -1:
            res = [0, 1]
        elif leftOrRight == 0:
            res = [1, 0]
        elif leftOrRight == 1:
            res = [0, -1]
    elif compareArrays(currentDirection, [0, -1]):
        if leftOrRight == -1:
            res = [-1, 0]
        elif leftOrRight == 0:
            res = [0, 1]
        elif leftOrRight == 1:
            res = [1, 0]
    print("result = " + str(res))
    return res

def changeDirection(leftOrRight):
    global currentDirection
    currentDirection = getAbsoluteDirection(leftOrRight)


def getDeviceRotation():
    yaw = hub.motion_sensor.get_yaw_angle()
    if yaw < 1:
        yaw = 360 - abs(yaw)
    return yaw

# if you want to turn left by 'degree' the this calculates your aimed angle
def getRotationGoalLeft(currentRotation, degree):
    goal = currentRotation - degree
    if goal < 0:
        goal = goal + 360
    return goal

# if you want to turn right by 'degree' the this calculates your aimed angle
def getRotationGoalRight(currentRotation, degree):
    goal = currentRotation + degree
    if goal > 359:
        goal = goal - 360
    return goal

# defines how far the second angle is from the first angle
def getAngleDistance(first, second) -> int:
    res = 0
    if first > second:
        res = first - second
        if res > 180:
            res = second + 360 - first
    else:
        res = second - first
        if res > 180:
            res = first + 360 - second
    return res

# defines how fast the vehicle rotates, gets slower if rotation is almost done
def getTurnRotations(currentAngle, goal) -> float:
    rotations = 0
    if getAngleDistance(currentAngle, goal) > 30:
        rotations = MAX_TURN_ROTAIONS
    elif getAngleDistance(currentAngle, goal) > 20:
        rotations = MIN_TURN_ROTATIONS + (MAX_TURN_ROTAIONS - MIN_TURN_ROTATIONS) * 0.5
    elif getAngleDistance(currentAngle, goal) > 4:
        rotations = MIN_TURN_ROTATIONS
    else:
        rotations = ABSOLUTE_MIN_TURN_ROTATIONS
    return rotations

# defines the speed of the vehicle when it does it's rotation, gets slower if rotation is almost done
def getTurnSpeed(currentAngle, goal) -> int:
    speed = 0
    if getAngleDistance(currentAngle, goal) > 30:
        speed = MAX_TURN_SPEED
    elif getAngleDistance(currentAngle, goal) > 20:
        speed = MIN_TURN_SPEED + (MAX_TURN_SPEED - MIN_TURN_SPEED) * 0.5
    else:
        speed = MIN_TURN_SPEED
    return int(speed)

def getBestCorrectionDirection(current, goal) -> int:
    tempgoal = goal
    if goal < current:
        tempgoal = goal + 360
    tempres = tempgoal - current
    if tempres is 0:
        return 0
    if tempres < 180:
        return tempres
    else:
        return tempres - 360


def correction(toDegree):
    currentRotation = getDeviceRotation()
    while(getAngleDistance(currentRotation, toDegree) > (CORRECTION_ACCURACY + 3)):
        while getBestCorrectionDirection(currentRotation, toDegree) > (CORRECTION_ACCURACY + 3):
            #print("correction right")
            motorRight.run_for_rotations(-4 * CORRECTION_ROTATIONS, 4* CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
        while getBestCorrectionDirection(currentRotation, toDegree) < ( -1 * (CORRECTION_ACCURACY + 3)):
            #print("correction left")
            motorLeft.run_for_rotations(4 * CORRECTION_ROTATIONS, 4 * CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
    while(getAngleDistance(currentRotation, toDegree) > (CORRECTION_ACCURACY + 2)):
        while getBestCorrectionDirection(currentRotation, toDegree) > (CORRECTION_ACCURACY + 2):
            #print("correction right")
            motorRight.run_for_rotations(-2 * CORRECTION_ROTATIONS, 2* CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
        while getBestCorrectionDirection(currentRotation, toDegree) < ( -1 * (CORRECTION_ACCURACY + 2)):
            #print("correction left")
            motorLeft.run_for_rotations(2 * CORRECTION_ROTATIONS, 2 * CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
    while(getAngleDistance(currentRotation, toDegree) > CORRECTION_ACCURACY):
        while getBestCorrectionDirection(currentRotation, toDegree) > CORRECTION_ACCURACY:
            #print("correction right")
            motorRight.run_for_rotations(-1 * CORRECTION_ROTATIONS, CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
        while getBestCorrectionDirection(currentRotation, toDegree) < ( -1 * CORRECTION_ACCURACY):
            #print("correction left")
            motorLeft.run_for_rotations(1 * CORRECTION_ROTATIONS, CORRECTION_SPEED)
            currentRotation = getDeviceRotation()

# toDegree is absolute angle in degree, direction < 0 is left and direction > 0 is right
def rotate(toDegree, direction):
    currentRotation = getDeviceRotation()
    print("Current rotation:" + str(currentRotation))
    print("Goal: " + str(toDegree))
    if direction > 0:
        while (currentRotation - toDegree) > ROTATION_ACCURACY or ( (currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorRight.run_for_rotations(
                -1 * getTurnRotations(currentRotation, toDegree),
                getTurnSpeed(currentRotation, toDegree),
            )
        correction(toDegree)
    elif direction < 0:
        while (currentRotation - toDegree) > ROTATION_ACCURACY or ( (currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorLeft.run_for_rotations(
                1 * getTurnRotations(currentRotation, toDegree),
                getTurnSpeed(currentRotation, toDegree),
            )
        correction(toDegree)
    currentRotation = getDeviceRotation()


# does turn the vehicle around for 180 degree
def turnAround():
    currentRotation = getDeviceRotation()
    plannedRotation = getRotationGoalRight(currentRotation, 90)
    toDegree = plannedRotation
    while (currentRotation - toDegree) > ROTATION_ACCURACY or ( (currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
        currentRotation = getDeviceRotation()
        motorRight.run_for_rotations(
            -1 * getTurnRotations(currentRotation, toDegree),
            getTurnSpeed(currentRotation, toDegree),
        )
    correction(toDegree)
    currentRotation = getDeviceRotation()
    plannedRotation = getRotationGoalRight(currentRotation, 90)
    toDegree = plannedRotation
    while (currentRotation - toDegree) > ROTATION_ACCURACY or ( (currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
        currentRotation = getDeviceRotation()
        motorLeft.run_for_rotations(
            -1 * getTurnRotations(currentRotation, toDegree),
            getTurnSpeed(currentRotation, toDegree),
        )
    correction(toDegree)
    currentRotation = getDeviceRotation()


def checkIfNodeInFront():
    if checkColor():
        print("found")
        searching = False
        return True
    return False

def driveToNodeOnPosition(position, search):
    global currentNode
    global lastDestination
    global currentDestination
    if((search is True) and checkIfNodeInFront()):
        return
    rot = getDeviceRotation()
    way = nodes[currentNode][position]
    print("Current node: " + str(currentNode) + " last node: " + str(lastDestination) + " current destiantion: " + str(currentDestination) + " way: " + str(way))
    distance = way[3]
    step = 25
    while distance > step:
        motors.move(step, "cm", 0, 30)
        distance = distance - step
        if((search is True) and checkIfNodeInFront()):
            return
        correction(rot)
    motors.move(distance, "cm", 0, 30)
    correction(rot)
    lastDestination = currentNode
    currentNode = way[2]

def driveToNode(direction, search):
    driveToNodeOnPosition(directionPosition(direction[0], direction[1]), search)

def checkColor():
    return colorSensor.get_color() == "red"


def getLeastTraversedPartnerPosition(nodeid, traversions):
    node = nodes[nodeid]
    res = (-1, -1)
    minTrav = 9999999999
    minDist = 9999999999
    for i in range(1,5):
        edge = node[i]
        destination = edge[2]
        distance = edge[3]
        if destination != -1:
            if traversions[destination] < minTrav or (traversions[destination] == minTrav and distance < minDist):
                res = (destination ,i)
                minTrav = traversions[destination]
                minDist = distance
    return res


def initDistanceDict():
    global distance
    global predecesour
    distance = {}
    predecesour = {}
    for i in range(0, len(nodes)):
        distance[i] = []
        predecesour[i] = {}
        for j in range(0, len(nodes)):
            if j != i:
                distance[i].append(9999999999)
                predecesour[i][j] = -1
            else:
                distance[i].append(0)
                predecesour[i][j] = i

#Path Bestandteil = (Zielknoten, Kantennumer, Distanz)
def createPathToNode(start, goal):
    global distance
    global predecesour
    q = []
    for i in range(0, len(nodes)):
        q.append(i)

    while len(q) > 0:
        v = q[0]
        for j in q:
            if(distance[start][j] < distance[start][v]):
                v = j
        q.remove(v)
        for w in range(1, len(nodes[v])):
            edgew = nodes[v][w]
            nodew = edgew[2]
            if(q.count(nodew) > 0):
                if (distance[start][v] + edgew[3]) < distance[start][nodew]:
                    distance[start][nodew] = distance[start][v] + edgew[3]
                    predecesour[start][nodew] = v

    #print(distance)
    #print(predecesour)
    res = []
    v = goal
    while v != start:
        vgoal = v
        v = predecesour[start][vgoal]
        for k in range(1, len(nodes[v])):
            if nodes[v][k][2] == vgoal:
                distance = nodes[v][k][3]
                res.insert(0, [vgoal, k, distance])
                break
    return res

def createPathTroughLabyrinth():
    current = currentNode
    distance = 0
    traversions = {}
    traversednodes = 0
    path = []
    for n in nodes.keys():
        traversions[n] = 0
    while traversednodes < len(nodes):
        if traversions[current] == 0:
            traversednodes += 1
        traversions[current] += 1
        nextPosition = getLeastTraversedPartnerPosition(current, traversions)
        distance = nodes[current][nextPosition[1]][3]
        path.append([nextPosition[0],nextPosition[1], distance])
        current = nodes[current][nextPosition[1]][2]
    return path

def turnToEdge(currentRotation, position):
    if compareArrays(currentDirection, [1,0]):
        if position == 2:
            goal = getRotationGoalRight(currentRotation, 90)
            rotate(goal, 1)
            changeDirection(1)
        if position == 3:
            turnAround()
            changeDirection(0)
        if position == 4:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)
            changeDirection(-1)
    elif compareArrays(currentDirection, [0,1]):
        if position == 3:
            goal = getRotationGoalRight(currentRotation, 90)
            rotate(goal, 1)
            changeDirection(1)
        if position == 4:
            turnAround()
            changeDirection(0)
        if position == 1:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)
            changeDirection(-1)
    elif compareArrays(currentDirection, [-1,0]):
        if position == 4:
            goal = getRotationGoalRight(currentRotation, 90)
            rotate(goal, 1)
            changeDirection(1)
        if position == 1:
            turnAround()
            changeDirection(0)
        if position == 2:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)
            changeDirection(-1)
    elif compareArrays(currentDirection, [0,-1]):
        if position == 1:
            goal = getRotationGoalRight(currentRotation, 90)
            rotate(goal, 1)
            changeDirection(1)
        if position == 2:
            turnAround()
            changeDirection(0)
        if position == 3:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)
            changeDirection(-1)


def liftTarget():
    for i in range(0, 10):
        motors.move(1, "cm", 0, 30)
"""
if should_morse:
    receive()
"""

if not len(nodes) > 1:
    import sys
    sys.exit(0)

# MAIN BEGINS HERE
aimedRotation = getDeviceRotation()
initDistanceDict()
startnode = 0
endnode = 4
path = createPathToNode(startnode, endnode)
visited = 0

while searching:
    print("path: " + str(path))
    if len(path) > visited:
        print("get position")
        position = path[visited][1]
        print("position: " + str(position))
        print("turn to edge start")
        turnToEdge(aimedRotation, position)
        print("turn to edge stop")
        print("get aimed rotation")
        aimedRotation = getDeviceRotation()
        print("aimed rotation: " + str(aimedRotation))
        print("start drive to node on postion")
        driveToNodeOnPosition(position, True)
        print("stop drive to node on postion")
        visited += 1
    else:
        searching = False

liftTarget()

visited = 0
initDistanceDict()
reversePath = createPathToNode(endnode, startnode)
currentNode = endnode
aimedRotation = getDeviceRotation()
while len(reversePath) > visited:
    print("reversed path: " + str(reversePath))
    if len(reversePath) > visited:
        print("get position")
        position = reversePath[visited][1]
        print("position: " + str(position))
        print("turn to edge start")
        turnToEdge(aimedRotation, position)
        print("turn to edge stop")
        print("get aimed rotation")
        aimedRotation = getDeviceRotation()
        print("aimed rotation: " + str(aimedRotation))
        print("start drive to node on postion")
        driveToNodeOnPosition(position, False)
        print("stop drive to node on postion")
        visited += 1
