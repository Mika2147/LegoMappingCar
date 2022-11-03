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

CORRECTION_SPEED = 0.02

MAX_SPEED_CM_MOVE = 8

ROTATION_ACCURACY = 2


areaMap = [] # TODO save the data
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

def getDeviceRotation() -> int:
    yaw = hub.motion_sensor.get_yaw_angle()
    if(yaw < 1):
        yaw = 360 - abs(yaw)
    return yaw

def getRotationGoalLeft(currentRotation, degree) -> int:
    goal = currentRotation - degree
    if(goal < 0):
        goal = goal + 360
    return goal

def getRotationGoalRight (currentRotation, degree) -> int:
    goal = currentRotation + degree
    if(goal > 359):
        goal = goal - 360
    return goal

def objectInFront() -> bool:
    frontDistance = distanceSensorFront.get_distance_cm()
    if frontDistance is not None:
        return frontDistance < MAX_FRONT_DISTANCE_CM

    return False


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


#NEW
def getTurnRotations(currentAngle, goal) -> float:
    rotations = 0
    if getAngleDistance(currentAngle, goal) > 30:
        rotations = MAX_TURN_ROTAIONS
    elif getAngleDistance(currentAngle, goal) > 15:
        rotations = MIN_TURN_ROTATIONS + (MAX_TURN_ROTAIONS - MIN_TURN_ROTATIONS) * 0.5
    else:
        rotations = MIN_TURN_ROTATIONS
    return rotations

#NEW
def getTurnSpeed(currentAngle, goal) -> int:
    speed = 0
    if getAngleDistance(currentAngle, goal) > 30:
        speed = MAX_TURN_SPEED
    elif getAngleDistance(currentAngle, goal) > 15:
        speed = MIN_TURN_SPEED + (MAX_TURN_SPEED - MIN_TURN_SPEED) * 0.5
    else:
        speed = MIN_TURN_SPEED
    return int(speed)



#TODO: new -> test this
#toDegree is absolute angle in degree, direction < 0 is left and direction > 0 is right
def rotate(toDegree, direction):
    currentRotation = getDeviceRotation()
    if direction > 0:
        while(currentRotation - toDegree) > ROTATION_ACCURACY or((currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorRight.run_for_rotations(-1 * getTurnRotations(currentRotation , toDegree), getTurnSpeed(currentRotation , toDegree))
    elif direction < 0:
        while(currentRotation - toDegree) > ROTATION_ACCURACY or((currentRotation - toDegree) < -1 * ROTATION_ACCURACY):
            currentRotation = getDeviceRotation()
            motorLeft.run_for_rotations(1 * getTurnRotations(currentRotation , toDegree), getTurnSpeed(currentRotation , toDegree))


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

aimedRotation = getDeviceRotation()

while mapping:
    motors.move(speedToGo(), 'cm', 0, 50)

    currentRotation = getDeviceRotation()

    if aimedRotation > currentRotation:
        print("correction right")
        rotate(aimedRotation, 1)
        currentRotation = getDeviceRotation()

    if aimedRotation < currentRotation:
        print("correction left")
        rotate(aimedRotation, -1)
        currentRotation = getDeviceRotation()

    distanceLeft = distanceSensorLeft.get_distance_cm()
    distanceRight = distanceSensorRight.get_distance_cm()

    frontHasObject = objectInFront()

    if frontHasObject:
        if distanceLeft is not None and distanceRight is not None:
            if distanceRight >= MAX_WALL_DISTANCE_CM:
                print("turn right")
                plannedRotation = getRotationGoalRight(currentRotation, 90)
                rotate(plannedRotation, 1)
                aimedRotation = plannedRotation
            elif distanceLeft >= MAX_WALL_DISTANCE_CM:
                print("turn left")
                plannedRotation = getRotationGoalLeft(currentRotation, 90)
                rotate(plannedRotation, -1)
                aimedRotation = plannedRotation
            else:
                plannedRotation = getRotationGoalLeft(currentRotation, 180)
                turnAround()
                aimedRotation = plannedRotation

        else:
            print("correction distance is NONE")


