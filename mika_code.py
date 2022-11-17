from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, ForceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
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

MAPSIZE = 50


areaMap = []
currentLocation = (int(MAPSIZE / 2), int(MAPSIZE / 2))
startingLocation = currentLocation
#defines the direction the vehicle is moving in the map
currentDirection = (1,0)
mapping = True

# Create your objects here.
hub = MSHub()

motorLeft = Motor('A')
motorRight = Motor('B')
motors = MotorPair('A', 'B')

distanceSensorLeft = DistanceSensor('C')
distanceSensorRight = DistanceSensor('D')
distanceSensorFront = DistanceSensor('F')

currentRotation = 0
plannedRotation = 0

counter = 0

#initailizes the area map that saves all the waypoints
def initAreaMap():
    for w in range(0,MAPSIZE):
        row = []
        for h in range(0,MAPSIZE):
            row.append(0)
        areaMap.append(row)


def printAreaMap():
    print("-----------------------------------------------------------------------------------------")
    for w in areaMap:
        row = ""
        for h in w:
            row = row + str(h)
        row = row + "\n"
        print(row)

def logMoveToAreaMap(cm, direction):
    for i in range(0, cm):
        location = (currentLocation[0] + i * direction[0], currentLocation[1] + i * direction[1])
        areaMap[location[0]][location[1]] = 1

# leftOrRight: if turn left -> -1; turn right = 1; turn around -> 0
def changeDirection(leftOrRight):
    global currentDirection
    if currentDirection == (1,0):
        if leftOrRight == -1:
            currentDirection = (0, -1)
        elif leftOrRight == 0:
            currentDirection = (-1 , 0)
        elif currentDirection == 1:
            currentDirection = (0, 1)
    elif currentDirection == (0,1):
        if leftOrRight == -1:
            currentDirection = (1, 0)
        elif leftOrRight == 0:
            currentDirection = (0 , -1)
        elif currentDirection == 1:
            currentDirection = (-1, 0)
    elif currentDirection == (-1,0):     
        if leftOrRight == -1:
            currentDirection = (0, 1)
        elif leftOrRight == 0:
            currentDirection = (1 , 0)
        elif currentDirection == 1:
            currentDirection = (0, -1)
    elif currentDirection == (0,-1):
        if leftOrRight == -1:
            currentDirection = (-1, 0)
        elif leftOrRight == 0:
            currentDirection = (0 , 1)
        elif currentDirection == 1:
            currentDirection = (1, 0)

# measures the current rotation of the vehicle
def getDeviceRotation() -> int:
    yaw = hub.motion_sensor.get_yaw_angle()
    if(yaw < 1):
        yaw = 360 - abs(yaw)
    return yaw


# if you want to turn left by 'degree' the this calculates your aimed angle
def getRotationGoalLeft(currentRotation, degree) -> int:
    goal = currentRotation - degree
    if(goal < 0):
        goal = goal + 360
    return goal


# if you want to turn right by 'degree' the this calculates your aimed angle
def getRotationGoalRight (currentRotation, degree) -> int:
    goal = currentRotation + degree
    if(goal > 359):
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
            res =first + 360 - second
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
    while getBestCorrectionDirection(currentRotation, toDegree) < (-1* ROTATION_ACCURACY):
        print("correction left")
        motorLeft.run_for_rotations(1 * CORRECTION_ROTATIONS, CORRECTION_SPEED)
        currentRotation = getDeviceRotation()


#toDegree is absolute angle in degree, direction < 0 is left and direction > 0 is right
def rotate(toDegree, direction):
    currentRotation = getDeviceRotation()
    print("Current rotation:" + str(currentRotation))
    print("Goal: " + str(toDegree))
    if direction > 0:
        while(currentRotation - toDegree) > ROTATION_ACCURACY or((currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorRight.run_for_rotations(-1 * getTurnRotations(currentRotation , toDegree), getTurnSpeed(currentRotation , toDegree))
    elif direction < 0:
        while(currentRotation - toDegree) > ROTATION_ACCURACY or((currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorLeft.run_for_rotations(1 * getTurnRotations(currentRotation , toDegree), getTurnSpeed(currentRotation , toDegree))


# does turn the vehicle around for 180 degree
def turnAround():
    currentRotation = getDeviceRotation()
    toDegree = plannedRotation = getRotationGoalRight(currentRotation, 90)
    while(currentRotation - toDegree) > ROTATION_ACCURACY or((currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorRight.run_for_rotations(-1 * getTurnRotations(currentRotation , toDegree), getTurnSpeed(currentRotation , toDegree))
    toDegree = plannedRotation = getRotationGoalRight(currentRotation, 90)
    while(currentRotation - toDegree) > ROTATION_ACCURACY or((currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorLeft.run_for_rotations(-1 * getTurnRotations(currentRotation , toDegree), getTurnSpeed(currentRotation , toDegree))

# defines the speed of thevehicle, the closer a wall in front the slower it is
def speedToGo() -> int:
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
initAreaMap()
#printAreaMap()
aimedRotation = getDeviceRotation()

while mapping:
    currentSpeed = speedToGo()
    motors.move(currentSpeed, 'cm', 0, 50)

    #logMoveToAreaMap(currentSpeed, currentDirection)

    counter = counter + 1
    if(counter > 9):
        counter = 0
        #printAreaMap()

    currentRotation = getDeviceRotation()

    correction(aimedRotation)

    distanceLeft = distanceSensorLeft.get_distance_cm()
    distanceRight = distanceSensorRight.get_distance_cm()

    frontHasObject = objectInFront()

    if frontHasObject:
        if distanceLeft is not None and distanceRight is not None:
            print("Left: " + str(distanceLeft))
            print("Right: " + str(distanceRight))
            if distanceRight >= MAX_WALL_DISTANCE_CM:
                print("turn right")
                plannedRotation = getRotationGoalRight(currentRotation, 90)
                rotate(plannedRotation, 1)
                aimedRotation = plannedRotation
                changeDirection(1)
            elif distanceLeft >= MAX_WALL_DISTANCE_CM:
                print("turn left")
                plannedRotation = getRotationGoalLeft(currentRotation, 90)
                rotate(plannedRotation, -1)
                aimedRotation = plannedRotation
                changeDirection(-1)
            else:
                plannedRotation = getRotationGoalLeft(currentRotation, 180)
                turnAround()
                aimedRotation = plannedRotation
                changeDirection(0)

        elif distanceLeft is None:
            print("distasnceLeft is NONE")
        elif distanceRight is None:
            print("distanceRight is NONE")


