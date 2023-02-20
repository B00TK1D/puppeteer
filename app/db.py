import itertools


def init():
    global data, id_iter
    data = {
        "exploits": {},
        "flags": {},
        "teams": {},
        "boxes": {},
    }

    id_iter = itertools.count()