from mindstorms import (
   MSHub,
   Motor,
   MotorPair,
   ColorSensor,
   DistanceSensor,
)
from mindstorms.operator import not_equal_to

MAX_WALL_DISTANCE_CM = 40
MAX_FRONT_DISTANCE_CM = 5

MAX_TURN_ROTAIONS = 0.5
MIN_TURN_ROTATIONS = 0.05
ABSOLUTE_MIN_TURN_ROTATIONS = 0.01

MAX_TURN_SPEED = 50
MIN_TURN_SPEED = 5

CORRECTION_SPEED = 1
CORRECTION_ROTATIONS = 0.01

MAX_SPEED_CM_MOVE = 8

ROTATION_ACCURACY = 15
CORRECTION_ACCURACY = 0

TURN_AROUND_OFFSET = 0

SHORT = "."
LONG = "-"
EMPTY = "/"
BLANK = " "
NIL = ""
WHITESPACE = EMPTY

stop_sensor = ColorSensor("E")

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

def morse(character):
    key = str(character)
    if len(key) > 1:
        res = NIL
        for value in key:
            res += CODE[value] + BLANK
    else:
        res = CODE[key]
    return res

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

def send():
    for index in range(len(nodes)):
        data = nodes[index]
        morsed_word = NIL
        for element in data:
            morsed_value = NIL
            if isinstance(element, list):
                if element[2] == -1:
                    morsed_word = morse(element[0]) + WHITESPACE + morse(element[1]) + WHITESPACE * 2
                else:
                    for value in element:
                        for splitted in str(int(value)).strip().split(BLANK):
                            value = splitted
                        morsed_value = morse(value)
                        morsed_word += morsed_value + WHITESPACE
            print(morsed_word)
            display_morse(morsed_word, False)
            morsed_word = NIL
        display_morse("N", True)

# Knoten
# (id, Kante1, Kante2, Kante3, Kante 4)
# Kante
# (Richtung x, Richtung y, Zielknoten, Entfernung)
# -1 means unknown
# -2 means no destiantion
nodes = {}
"""
nodes = {
   0: [0, [1, 0, 1, 48.5], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]],
   1: [1, [1, 0, -1, -1], [0, 1, 2, 112.0], [-1, 0, 0, 48.5], [0, -1, -1, -1]],
   2: [2, [1, 0, 4, 48.0], [0, 1, -1, -1], [-1, 0, 3, 67.0], [0, -1, 1, 112.0]],
   4: [4, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, 2, 48.0], [0, -1, 5, 132.5]],
   5: [5, [1, 0, -1, -1], [0, 1, 4, 132.5], [-1, 0, -1, -1], [0, -1, -1, -1]],
}
"""

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
    if node in nodes:# NOTE also here i add an if check
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
    if tempres == 0:
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

def driveToNode(direction):
    global currentNode
    global lastDestination
    global currentDestination
    rot = getDeviceRotation()
    way = nodes[currentNode][directionPosition(direction[0], direction[1])]
    print("Current node: " + str(currentNode) + " last node: " + str(lastDestination) + " current destiantion: " + str(currentDestination) + " way: " + str(way))
    distance = way[3]
    while distance > 5:
        motors.move(5, "cm", 0, 30)
        distance = distance - 5
        correction(rot)
    motors.move(distance, "cm", 0, 30)
    correction(rot)
    lastDestination = currentNode
    currentNode = way[2]



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
            if currentDistanceFromLastNode > 25:
                updateEdge(
                    currentNode,
                    currentDirection[0],
                    currentDirection[1],
                    currentDestination,
                    currentDistanceFromLastNode,
                )
                lastDestination = currentNode
                currentNode = currentDestination

            print("Updated nodes: \n" + str(nodes))
            currentDistanceFromLastNode = 0
            goalset = 0
            if distanceRight >= MAX_WALL_DISTANCE_CM:
                print("turn right")
                plannedRotation = getRotationGoalRight(currentRotation, 90)
                rotate(plannedRotation, 1)
                aimedRotation = plannedRotation

                if hasAlreadyCheckedDirection(currentNode, 1):
                    driveToNode(getAbsoluteDirection(1))
                else:
                    currentNode = currentDestination
                    nodeIdCounter = nodeIdCounter + 1
                    currentDestination = nodeIdCounter
                changeDirection(1)
                goalset = 1
            if distanceLeft >= MAX_WALL_DISTANCE_CM and goalset == 0:
                print("turn left")
                plannedRotation = getRotationGoalLeft(currentRotation, 90)
                rotate(plannedRotation, -1)
                aimedRotation = plannedRotation

                if hasAlreadyCheckedDirection(currentNode, -1):
                    driveToNode(getAbsoluteDirection(-1))
                else:
                    nodeIdCounter = nodeIdCounter + 1
                    currentDestination = nodeIdCounter
                changeDirection(-1)
                goalset = 1
            if goalset == 0:
                print("turn around")
                plannedRotation = getRotationGoalLeft(currentRotation, 180)
                turnAround()
                aimedRotation = plannedRotation

                driveToNode(getAbsoluteDirection(0))
                changeDirection(0)
                nodeIdCounter = nodeIdCounter + 1
                currentDestination = nodeIdCounter
                goalset = 1


        else:
            if distanceLeft is None:
                print("distasnceLeft is NONE")
            if distanceRight is None:
                print("distanceRight is NONE")

    if not_equal_to(stop_sensor.get_color(), None):
        mapping = not mapping

print("sending morse data")
send() # Send the Mapped Nodes D
