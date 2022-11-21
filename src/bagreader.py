from caromobject import Ball, Binfo
from balltracker import find_cue


def bag_reader(ball_bags, edges):
    b = [Ball(), Ball(), Ball()]
    for i, bag in enumerate(ball_bags):
        for ball in bag:
            object = Binfo(ball["frame"], ball["x"], ball["y"])
            b[i].insert_obj(object)

    for i in range(len(b)):
        b[i].add_move()

    cue, tar1, tar2 = find_cue(b[0], b[1], b[2])
    cue.id = 5
    tar1.id = 6
    tar2.id = 7

    eq1 = edges["TR"]
    eq2 = edges["TL"]
    eq3 = edges["BL"]
    eq4 = edges["BR"]

    cshline = [(eq1, eq2), (eq2, eq3), (eq3, eq4), (eq4, eq1)]
    
    return cue, tar1, tar2, cshline