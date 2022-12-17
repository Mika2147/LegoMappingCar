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


def generate_morse_codes():
    morse_codes = {
        "-": "-....-",  # Negative Numbers
        ".": ".-.-.-",  # Float Numbers
    }
    template = ["-", "-", "-", "-", "-"]
    morse_codes["0"] = "".join(template)
    for index in range(0, 5):
        template[index] = "."
        morse_codes[str(index + 1)] = "".join(template)
    for index in range(0, 4):
        template[index] = "-"
        morse_codes[str(index + 6)] = "".join(template)
    return morse_codes


CODE = generate_morse_codes()
SHORT = "." 
LONG = "-" 
EMPTY = "/"

def morse(character):
    key = str(character)
    if len(key) > 1:
        res = ""
        for value in key:
            res += CODE[value] + " "
    else:
        res = CODE[key]
    return res

def de_morse(morse_code):
    def compare(word):
        for key, value in CODE.items():
            if value == word: return key
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
        result.append(int(element) if float(
            element).is_integer() else float(element))
    return result

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
        if hub.left_button.is_pressed(): morsed_value += "."  # Adding a Short
        if hub.right_button.is_pressed(): morsed_value += "-"  # Adding a Long
        # Adding a Space
        if hub.left_button.is_pressed() and hub.left_button.is_pressed():
            counter += 1
            morsed_value += "//"
        if counter == 4: node[id].append(de_morse(morsed_value))  # Append Data to Node
        if button_force.is_pressed(): id += 1  # Next Node
        if button_force.is_pressed() and hub.left_button.is_pressed(): collecting = False  # stop
def main():
    for node, data in nodes.items():
        print(f"Der Knoten {node} hat folgende Elemente:")
        morsed_word = ""
        for element in data:
            morsed_value = ""
            if isinstance(element, list):
                for value in element:
                    for splitted in str(value).strip().split(" "):
                        splitted = float(splitted)
                        value = splitted if not splitted.is_integer() else int(splitted)
                    morsed_value = morse(value)
                    morsed_word += morsed_value + " // "
                #display_morse(morsed_word)
                print(f"{element} ==> {morsed_word} ==> {de_morse(morsed_word)}")
            morsed_word = ""
        #display_morse("N")

if __name__ == "__main__":
    main()
