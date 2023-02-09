from mindstorms import (
    MSHub,
    Motor,
    MotorPair,
    ColorSensor,
)
from mindstorms.operator import not_equal_to
import time

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

# =============================================
# ========  CACHING ===========================
# =============================================
# == Kommentiere die Zeile 32 und 33 aus. =====
# == Kommentiere Zeile 34 ein. ================
# =============================================

#nodes = {0: [0, [1, 0, 1, 48.5], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 1: [1, [1, 0, -1, -1], [0, 1, 2, 112.0], [-1, 0, 0, 48.5], [0, -1, -1, -1]], 2: [2, [1, 0, 4, 48.0], [0, 1, -1, -1], [-1, 0, 3, 67.0], [0, -1, 1, 112.0]], 3: [3, [1, 0, 2, 67.0], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 4: [4, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, 2, 48.0], [0, -1, 5, 132.5]], 5: [5, [1, 0, -1, -1], [0, 1, 4, 132.5], [-1, 0, -1, -1], [0, -1, -1, -1]]}
#nodes = {0: [0, [1,0,1,79.5],[0,1,-1,-1],[-1,0,-1,-1],[0,-1,-1,-1]], 1: [1, [1,0,-1,-1],[0,1,2,110.5],[-1,0,0,79.5],[0,-1,-1,-1]], 2: [2, [1,0,4,55.0],[0,1,-1,-1],[-1,0,3,58.5],[0,-1,1,110.5]], 3: [3, [1,0,2,58.5],[0,1,-1,-1],[-1,0,-1,-1],[0,-1,-1,-1]], 4: [4, [1,0,-1,-1],[0,1,-1,-1],[-1,0,2,55.0],[0,-1,5,119.0]], 5: [5, [1,0,-1,-1],[0,1,4,119.0],[-1,0,-1,-1],[0,-1,-1,-1]]}
nodes = open("data.json", "r").read()

# =============================================

distance = {}
predecesour = {}
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
            motorRight.run_for_rotations(-4 * CORRECTION_ROTATIONS, 4* CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
        while getBestCorrectionDirection(currentRotation, toDegree) < ( -1 * (CORRECTION_ACCURACY + 3)):
            motorLeft.run_for_rotations(4 * CORRECTION_ROTATIONS, 4 * CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
    while(getAngleDistance(currentRotation, toDegree) > (CORRECTION_ACCURACY + 2)):
        while getBestCorrectionDirection(currentRotation, toDegree) > (CORRECTION_ACCURACY + 2):
            motorRight.run_for_rotations(-2 * CORRECTION_ROTATIONS, 2* CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
        while getBestCorrectionDirection(currentRotation, toDegree) < ( -1 * (CORRECTION_ACCURACY + 2)):
            motorLeft.run_for_rotations(2 * CORRECTION_ROTATIONS, 2 * CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
    while(getAngleDistance(currentRotation, toDegree) > CORRECTION_ACCURACY):
        while getBestCorrectionDirection(currentRotation, toDegree) > CORRECTION_ACCURACY:
            motorRight.run_for_rotations(-1 * CORRECTION_ROTATIONS, CORRECTION_SPEED)
            currentRotation = getDeviceRotation()
        while getBestCorrectionDirection(currentRotation, toDegree) < ( -1 * CORRECTION_ACCURACY):
            motorLeft.run_for_rotations(1 * CORRECTION_ROTATIONS, CORRECTION_SPEED)
            currentRotation = getDeviceRotation()

# toDegree is absolute angle in degree, direction < 0 is left and direction > 0 is right
def rotate(toDegree, direction):
    currentRotation = getDeviceRotation()
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
        position = path[visited][1]
        turnToEdge(aimedRotation, position)
        aimedRotation = getDeviceRotation()
        driveToNodeOnPosition(position, True)
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
