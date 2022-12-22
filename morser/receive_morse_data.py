def receive():
    node = {}
    collecting = True
    id = 0
    b_empty = ColorSensor("B")
    d_next = ColorSensor("D")
    print("start collecting")
    import time
    morsed_value = NIL
    while collecting:
        node[id] = [id]
        counter = 0
        if hub.right_button.is_pressed():
            morsed_value += "."
            print(".")
            time.sleep(1)
        elif hub.left_button.is_pressed():
            morsed_value += "-"
            print("-")
            time.sleep(1)
        elif not_equal_to(b_empty.get_color(), None):
            morsed_value += " "
            print(" ")
            time.sleep(1)
        elif not_equal_to(d_next.get_color(), None):
            morsed_value += "/"
            print("/")
            time.sleep(1)
            counter += 0.5
        elif counter == 4: 
            print("next")
            node[id].append(de_morse(morsed_value))
        # TODO get missing sensor and finish following pseudocode
        # - if slash_counter == 4 then next list and list_counter += 1
        # - if list_counter == 4 then next node_id
        # - if missing_sensor.is_pressed() then finished collecting 
        else:
            print(morsed_value)
            hub.speaker.beep()
    print(morsed_value)
