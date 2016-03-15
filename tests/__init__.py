import platform

PYPY = platform.python_implementation() == 'PyPy'


def cross(*args):
    dim = len(args)
    if dim == 0:
        ret = []
    elif dim == 1:
        ret = [list(args[0][:])]
    elif dim == 2:
        ret = [[x, y] for x in args[0] for y in args[1]]
    else:
        ret = []
        left = cross(*args[:-1])
        right = list(args[-1][:])
        for x in left:
            for y in right:
                e = x[:]
                e.append(y)
                ret.append(e)
    return ret


def cross_kv(keys, values):
    return [{key: value for key in keys} for value in values]


def cross_dict(*args):
    dim = len(args)
    if dim == 0:
        ret = []
    elif dim == 1:
        ret = args[0]
    else:
        ret = []
        left = cross_dict(*args[:-1])
        right = args[-1]
        for x in left:
            for y in right:
                d = x.copy()
                d.update(y)
                ret.append(d)
    return ret
