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

MAX_WALL_DISTANCE_CM = 25
MAX_FRONT_DISTANCE_CM = 5

MAX_TURN_ROTAIONS = 0.5
MIN_TURN_ROTATIONS = 0.05

MAX_TURN_SPEED = 50
MIN_TURN_SPEED = 5

CORRECTION_SPEED = 1
CORRECTION_ROTATIONS = 0.01

MAX_SPEED_CM_MOVE = 8

ROTATION_ACCURACY = 2

TURN_AROUND_OFFSET = 0

# Knoten
# (id, Kante1, Kante2, Kante3, Kante 4)
# Kante
# (Richtung x, Richtung y, Zielknoten, Entfernung)
# -1 means unknown
# -2 means no destiantion
nodes = {}

# defines the direction the vehicle is moving in the map
currentDirection = [1, 0]
currentDistanceFromLastNode = 0
currentNode = 0
currentDestination = 1
lastDestination = 1
mapping = True
nodeIdCounter = 1

# Create your objects here.
hub = MSHub()

motorLeft = Motor("A")
motorRight = Motor("B")
motors = MotorPair("A", "B")

distanceSensorLeft = DistanceSensor("C")
distanceSensorRight = DistanceSensor("D")
distanceSensorFront = DistanceSensor("F")

currentRotation = 0
plannedRotation = 0

counter = 0


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


def createEmptyNode(myid):
    nodes[myid] = [ myid, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]]


def updateEdge(node_id, directionX, directionY, destinationId, distance):
    if destinationId not in nodes:
        createEmptyNode(destinationId)
    # TODO this check is not so optimal, better use the one, 2 lines up
    # elif nodes[destinationId] == None:
    #    createEmptyNode(destinationId)
    currentEdge = [ currentDirection[0], currentDirection[1], currentDestination, distance]
    reverseEdge = [ -currentDirection[0], -currentDirection[1], node_id, currentDistanceFromLastNode]
    # NOTE TUPLES ARE IMMUTABLE -> ERROR, use list's
    nodes[node_id][directionPosition(directionX, directionY)] = currentEdge
    if destinationId in nodes:
        # TODO still an Error
        # unknown key, so we want to read none or something unknown from to nodes.
        # destinationId is already checked so the method directionPostion() must be wrong
        nodes[destinationId][directionPosition(-directionX, -directionY)] = reverseEdge


def hasAlreadyCheckedDirection(node, leftOrRight) -> bool:
    ret = False
    # NOTE Function needs 2 param. there is just 1 :(
    absoluteDirection = getAbsoluteDirection(leftOrRight)
    pos = directionPosition(absoluteDirection[0], absoluteDirection[1])
    # don't really know the logic so i just made the
    # the second param optional.
    if node in nodes:  # NOTE also here i add an if check
        ret = nodes[node][pos][2] != -1
        print("Node " + str(node) + " pos: "+ str(pos) + " val: " + str(nodes[node][pos][2]))
    return ret

def compareArrays(first, second) -> bool:
    if len(first) != len(second):
        return False

    for i in range(0, len(first)):
        if first[i] != second[i]:
            return False
    
    return True

def getAbsoluteDirection(leftOrRight):
    #TODO: comparison doesnt work
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


# leftOrRight: if turn left -> -1; turn right = 1; turn around -> 0


def changeDirection(leftOrRight):
    global currentDirection
    currentDirection = getAbsoluteDirection(leftOrRight)


# measures the current rotation of the vehicle


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


# measures if there is an object in front of the vehicle
def objectInFront() -> bool:
    frontDistance = distanceSensorFront.get_distance_cm()
    if frontDistance is not None:
        return frontDistance < MAX_FRONT_DISTANCE_CM

    return False


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
    elif getAngleDistance(currentAngle, goal) > 15:
        rotations = MIN_TURN_ROTATIONS + (MAX_TURN_ROTAIONS - MIN_TURN_ROTATIONS) * 0.5
    else:
        rotations = MIN_TURN_ROTATIONS
    return rotations


# defines the speed of the vehicle when it does it's rotation, gets slower if rotation is almost done
def getTurnSpeed(currentAngle, goal) -> int:
    speed = 0
    if getAngleDistance(currentAngle, goal) > 30:
        speed = MAX_TURN_SPEED
    elif getAngleDistance(currentAngle, goal) > 15:
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
    while getBestCorrectionDirection(currentRotation, toDegree) > ROTATION_ACCURACY:
        print("correction right")
        motorRight.run_for_rotations(-1 * CORRECTION_ROTATIONS, CORRECTION_SPEED)
        currentRotation = getDeviceRotation()
    while getBestCorrectionDirection(currentRotation, toDegree) < ( -1 * ROTATION_ACCURACY):
        print("correction left")
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
    elif direction < 0:
        while (currentRotation - toDegree) > ROTATION_ACCURACY or ( (currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorLeft.run_for_rotations(
                1 * getTurnRotations(currentRotation, toDegree),
                getTurnSpeed(currentRotation, toDegree),
            )


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
    plannedRotation = getRotationGoalRight(currentRotation, 90)
    toDegree = plannedRotation
    while (currentRotation - toDegree) > ROTATION_ACCURACY or ( (currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
        currentRotation = getDeviceRotation()
        motorLeft.run_for_rotations(
            -1 * getTurnRotations(currentRotation, toDegree),
            getTurnSpeed(currentRotation, toDegree),
        )


# defines the speed of thevehicle, the closer a wall in front the slower it is


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


# MAIN BEGINS HERE
aimedRotation = getDeviceRotation()
createEmptyNode(0)

while mapping:
    currentSpeed = speedToGo()
    motors.move(currentSpeed, "cm", 0, 50)
    currentDistanceFromLastNode = currentDistanceFromLastNode + currentSpeed

    currentRotation = getDeviceRotation()

    correction(aimedRotation)

    distanceLeft = distanceSensorLeft.get_distance_cm()
    distanceRight = distanceSensorRight.get_distance_cm()

    frontHasObject = objectInFront()

    if frontHasObject:
        if distanceLeft is not None and distanceRight is not None:
            print("Left: " + str(distanceLeft))
            print("Right: " + str(distanceRight))
            updateEdge(
                currentNode,
                currentDirection[0],
                currentDirection[1],
                currentDestination,
                currentDistanceFromLastNode,
            )
            currentDistanceFromLastNode = 0
            goalset = 0
            if distanceRight >= MAX_WALL_DISTANCE_CM:
                if not hasAlreadyCheckedDirection(currentNode, 1):
                    print("turn right")
                    plannedRotation = getRotationGoalRight(currentRotation, 90)
                    rotate(plannedRotation, 1)
                    aimedRotation = plannedRotation
                    changeDirection(1)
                    lastDestination = currentNode
                    currentNode = currentDestination
                    nodeIdCounter = nodeIdCounter + 1
                    currentDestination = nodeIdCounter
                    goalset = 1
            if distanceLeft >= MAX_WALL_DISTANCE_CM and goalset == 0:
                if not hasAlreadyCheckedDirection(currentNode, -1):
                    print("turn left")
                    plannedRotation = getRotationGoalLeft(currentRotation, 90)
                    rotate(plannedRotation, -1)
                    aimedRotation = plannedRotation
                    changeDirection(-1)
                    lastDestination = currentNode
                    currentNode = currentDestination
                    nodeIdCounter = nodeIdCounter + 1
                    currentDestination = nodeIdCounter
                    goalset = 1
            if goalset == 0:
                print("turn around")
                plannedRotation = getRotationGoalLeft(currentRotation, 180)
                turnAround()
                aimedRotation = plannedRotation
                changeDirection(0)
                currentDistanceFromLastNode = (
                    currentDistanceFromLastNode + TURN_AROUND_OFFSET
                )
                lastDestination = currentNode
                currentNode = currentDestination
                currentDestination = lastDestination
                goalset = 1

            print("Updated nodes: \n" + str(nodes))

        else:
            if distanceLeft is None:
                print("distasnceLeft is NONE")
            if distanceRight is None:
                print("distanceRight is NONE")
