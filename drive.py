from mindstorms import (
    MSHub,
    Motor,
    MotorPair,
    ColorSensor,
    DistanceSensor,
    ForceSensor,
    App,
)
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import (
    greater_than,
    greater_than_or_equal_to,
    less_than,
    less_than_or_equal_to,
    equal_to,
    not_equal_to,
)
import math


MAX_TURN_ROTAIONS = 0.5
MIN_TURN_ROTATIONS = 0.05
ABSOLUTE_MIN_TURN_ROTATIONS = 0.01

MAX_TURN_SPEED = 50
MIN_TURN_SPEED = 5

CORRECTION_SPEED = 1
CORRECTION_ROTATIONS = 0.01

MAX_SPEED_CM_MOVE = 8

ROTATION_ACCURACY = 10
CORRECTION_ACCURACY = 1

# Knoten
# (id, Kante1, Kante2, Kante3, Kante 4)
# Kante
# (Richtung x, Richtung y, Zielknoten, Entfernung)
# -1 means unknown
# -2 means no destiantion
nodes = {0: [0, [1, 0, 1, 48.5], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 1: [1, [1, 0, -1, -1], [0, 1, 2, 112.0], [-1, 0, 0, 48.5], [0, -1, -1, -1]], 2: [2, [1, 0, 4, 48.0], [0, 1, -1, -1], [-1, 0, 3, 67.0], [0, -1, 1, 112.0]], 3: [3, [1, 0, 2, 67.0], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 4: [4, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, 2, 48.0], [0, -1, 5, 132.5]], 5: [5, [1, 0, -1, -1], [0, 1, 4, 132.5], [-1, 0, -1, -1], [0, -1, -1, -1]]}

# defines the direction the vehicle is moving in the map
currentDirection = [1, 0]
currentDistanceFromLastNode = 0
currentNode = 0
currentDestination = 1
searching = True

hub = MSHub()

motorLeft = Motor("A")
motorRight = Motor("B")
motors = MotorPair("A", "B")

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
    #TODO: rotate überarbeiten
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
    plannedRotation = getRotationGoalRight(currentRotation, 90)
    toDegree = plannedRotation
    while (currentRotation - toDegree) > ROTATION_ACCURACY or ( (currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
        currentRotation = getDeviceRotation()
        motorLeft.run_for_rotations(
            -1 * getTurnRotations(currentRotation, toDegree),
            getTurnSpeed(currentRotation, toDegree),
        )
    correction(toDegree)

def speedToGo():
    frontDistance = distanceSensorFront.get_distance_cm()
    if frontDistance is None:
        return 0
    elif frontDistance > 30:
        return MAX_SPEED_CM_MOVE
    elif frontDistance > 20:
        return MAX_SPEED_CM_MOVE / 2
    elif frontDistance > 10:
        return MAX_SPEED_CM_MOVE / 8
    else:
        return MAX_SPEED_CM_MOVE / 16
    

def checkIfGoalInFront():
    if checkColor():
        print("found")
        searching = False
        return True
    return False

def driveToNodeOnPosition(position):
    global currentNode
    global lastDestination
    global currentDestination
    if(checkIfGoalInFront()):
        return
    rot = getDeviceRotation()
    way = nodes[currentNode][position]
    print("Current node: " + str(currentNode) + " last node: " + str(lastDestination) + " current destiantion: " + str(currentDestination) + " way: " + str(way))
    distance = way[3]
    while distance > 5:
        motors.move(5, "cm", 0, 30)
        distance = distance - 5
        if(checkIfGoalInFront()):
            return
        correction(rot)
    motors.move(distance, "cm", 0, 30)
    correction(rot)
    lastDestination = currentNode
    currentNode = way[2]

def driveToNode(direction):
    driveToNodeOnPosition(directionPosition(direction[0], direction[1]))

def driveForCm(cm):
    global currentNode
    global currentDestination
    if(checkIfGoalInFront()):
        return
    rot = getDeviceRotation()
    print("Current node: " + str(currentNode) +  " current destiantion: " + str(currentDestination))
    distance = cm
    while distance > 5:
        motors.move(5, "cm", 0, 30)
        distance = distance - 5
        if(checkIfGoalInFront()):
            return
        correction(rot)
    motors.move(distance, "cm", 0, 30)
    correction(rot)



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




def createPath():
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
        if position == 3:
            turnAround()
        if position == 4:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)
    elif compareArrays(currentDirection, [0,1]):
        if position == 3:
            goal = getRotationGoalRight(currentRotation, 90)
            rotate(goal, 1)
        if position == 4:
            turnAround()
        if position == 1:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)
    elif compareArrays(currentDirection, [-1,0]):
        if position == 4:
            goal = getRotationGoalRight(currentRotation, 90)
            rotate(goal, 1)
        if position == 1:
            turnAround()
        if position == 2:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)
    elif compareArrays(currentDirection, [0,-1]):
        if position == 1:
            goal = getRotationGoalRight(currentRotation, 90)
            rotate(goal, 1)
        if position == 2:
            turnAround()
        if position == 3:
            goal = getRotationGoalLeft(currentRotation, 90)
            rotate(goal, -1)




# MAIN BEGINS HERE
aimedRotation = getDeviceRotation()
setInverted(True);

while True:
    driveForCm(2)
    wait_for_seconds(2)




