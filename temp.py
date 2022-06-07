import math

v0 = 16.0
v2 = 13.0

a1 = 7.5
a2 = 18.0

s = 100.0


class NoRoot(Exception):
    pass


class Crash(Exception):
    pass


def quad_equation_root(a, b, c):
    _d = b ** 2 - 4 * a * c

    if _d > 0:
        root = max(
            (-_b + math.sqrt(_d)) / (2 * a),
            (-_b - math.sqrt(_d)) / (2 * a)
        )
    elif _d == 0:
        root = -b / (2 * a)
    else:
        raise NoRoot

    return root


def


if __name__ == '__main__':
    _a = a1*a2 + a1**2
    _b = 2*a2*v0 + 2*a1*v0
    _c = v0**2 - v2**2 - 2*a2*s

    t = quad_equation_root(_a, _b, _c)
    if t < 0:
        # поздно тормозить
        raise Crash("out of track")

    v1 = v0 + a1*t
    v0_km = v0 * 60.0 * 60.0 / 1000
    v2_km = v2 * 60.0 * 60.0 / 1000
    v1_km = v1 * 60.0 * 60.0 / 1000
    s1 = v0 * t + (a1 * (t**2)) / 2
    s2 = s-s1
    print("v0 = %.5f кмч\ts = %.5f m\tv2 = %.5f кмч" % (v0_km, s, v2_km))
    print("t = %.5f c\ts1 = %.5f m\ts2 = %.5f m\tv1 = %.5f кмч" % (t, s1, s2, v1_km))
