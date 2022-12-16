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
    def compare(word):
        for key, value in CODE.items():
            if value == word:
                return key

    data = ""
    result = []
    for element in morse_code.split("//"):
        element = element.strip()
        if " " in element:
            for word in element.split(" "):
                data += str(compare(word))
            data += " "
        else:
            if len(element) > 1:
                data += str(compare(element)) + " "
    for element in data.strip().split(" "):
        element = float(element)
        result.append(element if str(element).split(".")[1] != "0" else int(element))
    return result


def display_morse(morse_code):
    character = []
    for character in morse_code:
        if character == "." or character == "-" or character == "/":
            hub.light_matrix.write(character)
        hub.left_button.wait_until_pressed()


def display_next(character):
    hub.light_matrix.write(character)
    hub.right_button.wait_until_pressed()


def receive():
    """
    TODO: NOT TESTED
    THIS METHOD IS 100% NOT WORKING
    THE LOGIC IS NOT DONE, JUST A SCRATCHY IDEA COLLECTION HOW IT COULD BE
    """
    node = {}
    collecting = True
    id = 0
    while collecting:
        node[id] = [id]
        morsed_value = ""
        counter = 0
        # Adding a Short
        if hub.left_button.is_pressed():
            morsed_value += "."
        # Adding a Long
        if hub.right_button.is_pressed():
            morsed_value += "-"
        # Adding a Space
        if hub.left_button.is_pressed() and hub.left_button.is_pressed():
            counter += 1
            morsed_value += "/"
        # Done with this Node
        if ForceSensor("E").is_pressed():
            id += 1
        # Collected a full Element, prepare and append it
        if counter == 4:
            demorsed_value = demorse(morsed_value)
            demorsed_prepared = demorsed_value.split(" ")
            node[id].append(demorsed_prepared)
        # Finished the Collecting
        if ForceSensor("E").is_pressed() and hub.left_button.is_pressed():
            collecting = False


def testing(to_morse, morsed_value="", next_value="", print_value=""):
    if TESTING:
        if to_morse:
            display_morse(morsed_value)
        else:
            display_next(next_value)
    else:
        print(print_value)


def main():
    for node, data in nodes.items():
        print("Der Knoten", node, "hat folgende Elemente:")
        morsed_word = ""
        for element in data:
            morsed_value = ""
            if isinstance(element, list):
                for value in element:
                    morsed_value = morse(value)
                    morsed_word += morsed_value + " // "
                testing(
                    True,
                    morsed_value=morsed_word,
                    print_value=f"{element} ==> {morsed_word} ==> {demorse(morsed_word)}",
                )
            morsed_word = ""
        testing(False, next_value="N", print_value="")


main()
