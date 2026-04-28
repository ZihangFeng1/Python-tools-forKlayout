# Ruby learning examples (yield, hash) converted to Python

import pya

instSection = {
    'cello': 'string',
    'clarinet': 'woodwind',
    'drum': 'percussion',
    'oboe': 'woodwind',
    'trumpet': 'brass',
    'violin': 'string'
}


def threeTimes(f):
    for _ in range(3):
        f()


threeTimes(lambda: print("Hello"))


def fibUpTo(max_val, f):
    i1, i2 = 1, 1        # parallel assignment
    while i1 <= max_val:
        f(i1)
        i1, i2 = i2, i1 + i2


fibUpTo(1000, lambda f: print(str(f), end=" "))
