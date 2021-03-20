from peloton.conf.settings import sim_config


def is_equal(a: float, b: float) -> bool:
    return abs(a - b) < sim_config.float_precision


def pull_down(v: float, dst: float):
    if v > dst and is_equal(v, dst):
        return dst

    return v


def pull_up(v: float, dst: float):
    if v < dst and is_equal(v, dst):
        return dst

    return v


def pull_to(v: float, dst: float):
    return dst if is_equal(v, dst) else v

