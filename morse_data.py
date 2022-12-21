#!/usr/bin/env python3

TESTING = False

if TESTING:
    from mindstorms import MSHub, ForceSensor
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

SHORT = "."
LONG = "-"
EMPTY = "/"


def generate_morse_codes():
    morse_codes = {
        "-": LONG + SHORT * 3 + LONG,   # Minus for Negative Values
        ".": (SHORT + LONG) * 3         # Dots for Floats
    }
    template = [LONG, LONG, LONG, LONG, LONG]
    morse_codes["0"] = "".join(template)
    for index in range(0, 5):
        template[index] = SHORT
        morse_codes[str(index + 1)] = "".join(template)
    for index in range(0, 4):
        template[index] = LONG
        morse_codes[str(index + 6)] = "".join(template)
        template[index] = LONG
    morse_codes["0"] = LONG   # Simplify '-----' to '-'
    morse_codes["1"] = SHORT  # Simplify '.....' to '.'
    return morse_codes


CODE = generate_morse_codes()


def morse(character):
    key = str(character)
    if len(key) > 1:
        res = ""
        for value in key:
            res += CODE[value] + " "
    else:
        res = CODE[key]
    return res

de_morse_counter = 0

def de_morse(morse_code):
    def compare(word):
        return list(CODE.keys())[list(CODE.values()).index(word)]

    data = ""
    res = []
    for element in morse_code.split(EMPTY + EMPTY):
        element = element.strip()
        if " " in element:
            for word in element.split(" "):
                data += str(compare(word))
            data += " "
        else:
            if len(element) >= 1:
                data += str(compare(element)) + " "
    shorten = False
    for element in data.strip().split(" "):
        if len(data.strip().split(" ")) == 2: 
            res.append(int(element) if float(element).is_integer() else float(element))
            shorten = True
        else: 
            res.append(int(element) if float(element).is_integer() else float(element))
            shorten = False 
    if shorten: 
        res.append(-1)
        res.append(-1)
        # res.append(int(element) if float(element).is_integer() else float(element))
    return res


def display_morse(morse_code):
    character = []
    for character in morse_code:
        if character == SHORT or character == LONG or character == EMPTY:
            hub.light_matrix.write(character)
        hub.left_button.wait_until_pressed()


def display(character):
    hub.light_matrix.write(character)
    hub.left_button.wait_until_pressed()


def receive():
    """
    TODO the logic is more or less done but not tested
    """
    node = {}
    collecting = True
    id = 0
    button_force = ForceSensor("E")
    while collecting:
        node[id] = [id]
        morsed_value = ""
        counter = 0
        if hub.left_button.is_pressed():
            morsed_value += SHORT
        if hub.right_button.is_pressed():
            morsed_value += LONG
        if hub.left_button.is_pressed() and hub.left_button.is_pressed():
            counter += 1
            morsed_value += EMPTY + EMPTY
        if counter == 4:
            node[id].append(de_morse(morsed_value))
        if button_force.is_pressed():
            id += 1
        if button_force.is_pressed() and hub.left_button.is_pressed():
            collecting = False


def main():
    reconstructed = {}
    for node, data in nodes.items():
        # print(f"Der Knoten {node} hat folgende Elemente:", end="")
        reconstructed[node] = [node]
        morsed_word = ""
        for element in data:
            morsed_value = ""
            if isinstance(element, list):
                if element[2] == -1:
                    morsed_word = morse(element[0]) + " // " + morse(element[1]) + " // // "
                else: 
                    for value in element:
                        for splitted in str(value).strip().split(" "):
                            splitted = float(splitted)
                            value = splitted if not splitted.is_integer() else int(splitted)
                        morsed_value = morse(value)
                        morsed_word += morsed_value + " // "
                # display_morse(morsed_word)
                # print(f"{element} ==> {morsed_word} ==> {de_morse(morsed_word)}")
                reconstructed[node].append(de_morse(morsed_word))
            # print(morsed_word)
            morsed_word = ""
        # display_morse("N")
    print("ORIGINAL DATA\n", nodes)
    print("MORSED AND PREPARED DATA\n", reconstructed)


if __name__ == "__main__":
    main()
