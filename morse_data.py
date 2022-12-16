#!/usr/bin/env python3

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

hub = MSHub()

# Knoten
# (id, Kante1, Kante2, Kante3, Kante 4)
# Kante
# (Richtung x, Richtung y, Zielknoten, Entfernung)
# -1 means unknown
# -2 means no destiantion
nodes = {
    0: [0, [1, 0, 1, 48.5], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]],
    1: [1, [1, 0, -1, -1], [0, 1, 2, 112.0], [-1, 0, 0, 48.5], [0, -1, -1, -1]],
    2: [2, [1, 0, 4, 48.0], [0, 1, -1, -1], [-1, 0, 3, 67.0], [0, -1, 1, 112.0]],
    3: [3, [1, 0, 2, 67.0], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]],
    4: [4, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, 2, 48.0], [0, -1, 5, 132.5]],
    5: [5, [1, 0, -1, -1], [0, 1, 4, 132.5], [-1, 0, -1, -1], [0, -1, -1, -1]],
}

CODE = {
    " ": "_",
    "'": ".----.",
    "(": "-.--.-",
    ")": "-.--.-",
    ",": "--..--",
    "-": "-....-",
    ".": ".-.-.-",
    "/": "-..-.",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ":": "---...",
    ";": "-.-.-.",
    "?": "..--..",
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "_": "..--.-",
}


def morse(character):
    key = str(int(character))
    if len(key) > 1:
        res = ""
        for value in key:
            res += CODE[value]
    else:
        res = CODE[key]

    return res


def demorse(morse_code):
    for key, value in CODE.items():
        if value == morse_code:
            return key


def display(morse_code):
    character = []
    for character in morse_code:
        if character == "." or character == "-":
            hub.light_matrix.write(character)
        hub.left_button.wait_until_pressed()


def main():
    for node, data in nodes.items():
        print("Der Knoten", node, "hat folgende Elemente:")
        for element in data:
            if isinstance(element, list):
                for value in element:
                    morsed_value = morse(value)
                    display(morsed_value)
                    print(morsed_value, " -> ", value)
                print()
        print()


main()

"""
Der Knoten 0 hat folgende Elemente:
[1, 0, 1, 48.5]
[0, 1, -1, -1]
[-1, 0, -1, -1]
[0, -1, -1, -1]

Der Knoten 1 hat folgende Elemente:
[1, 0, -1, -1]
[0, 1, 2, 112.0]
[-1, 0, 0, 48.5]
[0, -1, -1, -1]

Der Knoten 2 hat folgende Elemente:
[1, 0, 4, 48.0]
[0, 1, -1, -1]
[-1, 0, 3, 67.0]
[0, -1, 1, 112.0]

Der Knoten 3 hat folgende Elemente:
[1, 0, 2, 67.0]
[0, 1, -1, -1]
[-1, 0, -1, -1]
[0, -1, -1, -1]

Der Knoten 4 hat folgende Elemente:
[1, 0, -1, -1]
[0, 1, -1, -1]
[-1, 0, 2, 48.0]
[0, -1, 5, 132.5]

Der Knoten 5 hat folgende Elemente:
[1, 0, -1, -1]
[0, 1, 4, 132.5]
[-1, 0, -1, -1]
[0, -1, -1, -1]
"""

"""
Der Knoten 0 hat folgende Elemente:
.---- ----- .---- ....----..
----- .---- -....-.---- -....-.----
-....-.---- ----- -....-.---- -....-.----
----- -....-.---- -....-.---- -....-.----

Der Knoten 1 hat folgende Elemente:
.---- ----- -....-.---- -....-.----
----- .---- ..--- .----.----..---
-....-.---- ----- ----- ....----..
----- -....-.---- -....-.---- -....-.----

Der Knoten 2 hat folgende Elemente:
.---- ----- ....- ....----..
----- .---- -....-.---- -....-.----
-....-.---- ----- ...-- -....--...
----- -....-.---- .---- .----.----..---

Der Knoten 3 hat folgende Elemente:
.---- ----- ..--- -....--...
----- .---- -....-.---- -....-.----
-....-.---- ----- -....-.---- -....-.----
----- -....-.---- -....-.---- -....-.----

Der Knoten 4 hat folgende Elemente:
.---- ----- -....-.---- -....-.----
----- .---- -....-.---- -....-.----
-....-.---- ----- ..--- ....----..
----- -....-.---- ..... .----...--..---

Der Knoten 5 hat folgende Elemente:
.---- ----- -....-.---- -....-.----
----- .---- ....- .----...--..---
-....-.---- ----- -....-.---- -....-.----
----- -....-.---- -....-.---- -....-.----
"""
