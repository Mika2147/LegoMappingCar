from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, ForceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math


MAX_WALL_DISTANCE_CM = 50
MAX_FRONT_DISTANCE_CM = 5

TURN_SPEED = 0.1
CORRECTION_SPEED = 0.02

MAX_SPEED_CM_MOVE = 8

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

def getDeviceRotation():
    yaw = hub.motion_sensor.get_yaw_angle()
    if(yaw < 1):
        yaw = 360 - abs(yaw)
    return yaw

def getRotationGoalLeft(currentRotation, degree):
    goal = currentRotation - degree
    if(goal < 0):
        goal = goal + 360
    return goal

def getRotationGoalRight (currentRotation, degree):
    goal = currentRotation + degree
    if(goal > 359):
        goal = goal - 360
    return goal

def objectInFront():
    frontDistance = distanceSensorFront.get_distance_cm()
    if frontDistance is not None:
        return frontDistance < MAX_FRONT_DISTANCE_CM
    
    return False


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

aimedRotation = getDeviceRotation()

while mapping:
    motors.move(speedToGo(), 'cm', 0, 50)

    currentRotation = getDeviceRotation()

    while aimedRotation > currentRotation:
        print("correction right")
        motorRight.run_for_rotations(-1 * CORRECTION_SPEED, 10)
        currentRotation = getDeviceRotation()

    while aimedRotation < currentRotation:
        print("correction left")
        motorLeft.run_for_rotations(1 * CORRECTION_SPEED, 10)
        currentRotation = getDeviceRotation()

    distanceLeft = distanceSensorLeft.get_distance_cm()
    distanceRight = distanceSensorRight.get_distance_cm()

    frontHasObject = objectInFront()
    
    if frontHasObject: 
        if distanceLeft is not None and distanceRight is not None:
            if distanceRight >= MAX_WALL_DISTANCE_CM:
                print("turn right")
                plannedRotation = getRotationGoalRight(currentRotation, 90)
                while(currentRotation - plannedRotation) > 2 or((currentRotation - plannedRotation) < -2):
                    print(" --> turn right")
                    currentRotation = getDeviceRotation()
                    motorRight.run_for_rotations(-1 * TURN_SPEED, 50)
                aimedRotation = currentRotation
            elif distanceLeft >= MAX_WALL_DISTANCE_CM:
                print("turn left")
                plannedRotation = getRotationGoalLeft(currentRotation, 90)
                while(currentRotation - plannedRotation) > 2 or((currentRotation - plannedRotation) < -2):
                    print(" --> turn left")
                    currentRotation = getDeviceRotation()
                    motorLeft.run_for_rotations(1 * TURN_SPEED, 50)
                aimedRotation = currentRotation
            elif distanceRight >= MAX_WALL_DISTANCE_CM and distanceLeft >= MAX_WALL_DISTANCE_CM:
                print("Sackgasse") # TODO implement a 180° turnaround
            else:
                print("correction distance is to big")
        else:
            print("correction distance is NONE")


