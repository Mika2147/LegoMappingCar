def receive():
    node = {}
    collecting = True
    node_id = 0
    b_empty = ColorSensor("B")
    d_next = ColorSensor("D")
    f_id = ColorSensor("F")
    print("start collecting")
    import time
    morsed_value = NIL
    counter = 0
    while collecting:
        node[node_id] = [node_id]
        if hub.right_button.is_pressed():
            morsed_value += "."
            time.sleep(1)
        elif hub.left_button.is_pressed():
            morsed_value += "-"
            time.sleep(1)
        elif not_equal_to(b_empty.get_color(), None):
            morsed_value += " "
            time.sleep(1)
        elif not_equal_to(d_next.get_color(), None):
            morsed_value += "/"
            time.sleep(1)
            counter += 1
        elif not_equal_to(f_id.get_color(), None):
            node[node_id].append(de_morse(morsed_value))
            print(de_morse(morsed_value))
            morsed_value = NIL
        else:
            print(morsed_value)
            if counter == 12:
                node[node_id].append(de_morse(morsed_value))
                node_id += 1
                print("node id + 1", node_id)
                counter = 0
            hub.speaker.beep()
    print(morsed_value)
