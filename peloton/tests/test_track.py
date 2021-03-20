from peloton.common.math import is_equal
from peloton.models.track import Sector


def test_curvature_straigt(straight_200: Sector):
    assert straight_200.curvature == 0.0


def test_curvature_max(max_curve_180: Sector, max_curve_90: Sector, max_curve_60: Sector):
    assert max_curve_180.curvature == 1.0
    assert max_curve_90.curvature == 1.0
    assert max_curve_60.curvature == 1.0


def test_curvature_max_inverse(max_curve_180: Sector, max_curve_90: Sector, max_curve_60: Sector):
    max_curve_180.corner *= -1
    max_curve_90.corner *= -1
    max_curve_60.corner *= -1
    assert max_curve_180.curvature == 1.0
    assert max_curve_90.curvature == 1.0
    assert max_curve_60.curvature == 1.0


def test_curvature_semi(semi_curve_180: Sector, semi_curve_90: Sector, semi_curve_30: Sector):
    assert semi_curve_180.curvature == 0.5
    assert semi_curve_90.curvature == 0.5
    assert semi_curve_30.curvature == 0.5


def test_curvature_semi_inverse(semi_curve_180: Sector, semi_curve_90: Sector, semi_curve_30: Sector):
    semi_curve_180.corner *= -1
    semi_curve_90.corner *= -1
    semi_curve_30.corner *= -1
    assert semi_curve_180.curvature == 0.5
    assert semi_curve_90.curvature == 0.5
    assert semi_curve_30.curvature == 0.5


def test_curvature_low(low_curve_180: Sector):
    assert is_equal(low_curve_180.curvature, 0.25)


def test_curvature_high(high_curve_180: Sector):
    assert is_equal(high_curve_180.curvature, 0.75)
