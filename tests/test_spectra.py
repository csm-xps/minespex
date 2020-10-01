import pytest
import numpy as np
from minespex.io.scienta import read
from minespex.base.spectra import Spectra, Scienta


def test_Spectra():
    try:
        s = Spectra()
    except TypeError:
        # A TypeError should be raised if an attempt is made to instantiate
        # an abstract base class.
        pass
    else:
        assert False, \
            "An attempt to construct a Spectra object should raise an error."


def test_Scienta():
    s1, s2 = read("data/scienta2D.txt")
    sint = s1.integrate_along("Y-Scale [mm]")
    uniqueDim = set(sint.dim.values())
    assert len(uniqueDim) == 1
    assert sint.axis("Binding Energy [eV]") == 0
    assert np.allclose(sint.scale("Binding Energy [eV]"), (624, 625))
    assert np.allclose(sint.data, [1.5, 3.5])

    s1, = read("data/scienta3D.txt")
    sint = s1.integrate_along("Y-Scale [mm]")
    uniqueDim = set(sint.dim.values())
    assert len(uniqueDim) == 2
    assert sint.axis("Binding Energy [eV]") == 0
    assert sint.axis("Seq. Iteration[a.u.]") == 1
    assert np.allclose(sint.scale("Binding Energy [eV]"), [624, 625, 626, 627])
    assert np.allclose(sint.scale("Seq. Iteration[a.u.]"), [1, 2])
    assert np.allclose(sint.data,
        [[ 1.9286449, 13.9286449],
         [ 4.9286449, 16.9286449],
         [ 7.9286449, 19.9286449],
         [10.9286449, 22.9286449]])

    sint = s1.integrate_along("Seq. Iteration[a.u.]")
    uniqueDim = set(sint.dim.values())
    assert len(uniqueDim) == 2
    assert sint.axis("Binding Energy [eV]") == 0
    assert sint.axis("Y-Scale [mm]") == 1
    assert np.allclose(sint.scale("Binding Energy [eV]"), [624, 625, 626, 627])
    assert np.allclose(sint.scale("Y-Scale [mm]"), [1.234, 5.678, 9.012])
    assert np.allclose(sint.data,
        [[ 7.,  8.,  9.],
         [10., 11., 12.],
         [13., 14., 15.],
         [16., 17., 18.]])
