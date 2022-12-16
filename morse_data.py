#!/usr/bin/env python3

TESTING = False 

if TESTING: 
    from mindstorms import MSHub
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
    key = str(character)
    if len(key) > 1:
        res = ""
        for value in key:
            res += CODE[value] + " "
    else:
        res = CODE[key]

    return res


def demorse(morse_code):
    for key, value in CODE.items():
        if value == morse_code:
            return key


def display_morse(morse_code):
    character = []
    for character in morse_code:
        if character == "." or character == "-":
            hub.light_matrix.write(character)
        hub.left_button.wait_until_pressed()


def display_next(character):
    hub.light_matrix.write(character)
    hub.right_button.wait_until_pressed()


def main():
    for node, data in nodes.items():
        print("Der Knoten", node, "hat folgende Elemente:")
        for element in data:
            if isinstance(element, list):
                for value in element:
                    morsed_value = morse(value)
                    if TESTING:
                        display_morse(morsed_value)
                    print(value, "\t==>\t", morsed_value)
                if TESTING:
                    display_next("E")
                print()

        if TESTING:
            display_next("N")

        print()


main()
