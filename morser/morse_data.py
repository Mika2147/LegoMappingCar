from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math, time

hub = MSHub()

TESTING = False

try:
    b_empty = ColorSensor("B")
    d_next = ColorSensor("D")
    f_id = ColorSensor("F")
except Exception:
    print("Not every Sensor is correct pluged in!")
    import sys
    sys.exit(0)

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
BLANK = " "
NIL = ""
# WHITESPACE = "//"
WHITESPACE = EMPTY

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

def de_morse(morse_code):
    def compare(word):
        return list(CODE.keys())[list(CODE.values()).index(word)]

    data = NIL
    res = []
    for element in morse_code.split(EMPTY):
        element = element.strip()
        if BLANK in element:
            for word in element.split(BLANK):
                data += str(compare(word))
            data += BLANK
        else:
            if len(element) >= 1:
                data += str(compare(element)) + BLANK
    shorten = False
    for element in data.strip().split(BLANK):
        if len(data.strip().split(BLANK)) == 2:
            res.append((element))
            shorten = True
        else:
            res.append((element))
            shorten = False

    if shorten:
        res.append(-1)
        res.append(-1)
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


def receive():
    node, node_id = {}, 0
    node[node_id] = [node_id]
    collecting = True
    morsed_value = NIL
    waiting_counter = 0
    while collecting:
        if hub.right_button.is_pressed():
            morsed_value += SHORT
            time.sleep(1)
            display_morse("S", False)
            wainting_counter = 0
        elif hub.left_button.is_pressed():
            morsed_value += LONG
            time.sleep(1)
            display_morse("L", False)
            wainting_counter = 0
        elif not_equal_to(b_empty.get_color(), None):
            morsed_value += BLANK
            time.sleep(1)
            display_morse("_", False)
            wainting_counter = 0
        elif not_equal_to(d_next.get_color(), None):
            morsed_value += WHITESPACE
            time.sleep(1)
            display_morse("/", False)
            wainting_counter = 0
        elif not_equal_to(f_id.get_color(), None):
            wainting_counter += 1
            if len(morsed_value) > 1:
                tmp = de_morse(morsed_value)
                morsed_value = NIL
                node[node_id].append(tmp)
                print(tmp, node)
        else:
            waiting_counter += 1
            print(morsed_value, node, waiting_counter)
            hub.speaker.beep()
            if len(node[node_id]) == 5:
                node_id += 1
            if waiting_counter == 20: 
                waiting_counter = 0
                collecting = False
                display_morse("F")


def send():
    for _, data in nodes.items():
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
            display_morse(morsed_word)
            morsed_word = NIL
        display_morse("N")

# send()
receive()
