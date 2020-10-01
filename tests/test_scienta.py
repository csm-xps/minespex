import pytest
import numpy as np
from minespex.io.scienta import read

def test_read_2d():
    # expected interface
    spectra = read("data/scienta2D.txt")
    # test the right number of spectra were read
    assert len(spectra) == 2, "Expected two spectra collections."
    #
    s1, s2 = spectra
    assert s1.axis("Binding Energy [eV]") == 0
    assert s1.axis(1) == 0, "1-index to 0-index broken."
    assert np.allclose(s1.scale("Binding Energy [eV]"), (624, 625)), \
        f"Binding energies don't match: {s1.scale('Binding Energy [eV]')}"
    assert s1.axis("Y-Scale [mm]") == 1
    assert s1.axis(2) == 1, "1-index to 0-index broken."
    assert np.allclose(s1.scale("Y-Scale [mm]"), (1.234, 5.678))
    assert s1.attributes == {"Region Name": "foo",
                             "Energy Step": 1,
                             "Run Mode Information": {}}, \
        f"s1.attributes = {s1.attributes}."
    assert np.allclose(s1.data, [[1, 2], [3, 4]])

    assert s2.axis("Binding Energy [eV]") == 0
    assert s2.axis(1) == 0, "1-index to 0-index broken."
    assert np.allclose(s2.scale("Binding Energy [eV]"), (148, 148.5))
    assert s2.axis("Y-Scale [mm]") == 1
    assert s2.axis(2) == 1, "1-index to 0-index broken."
    assert np.allclose(s2.scale("Y-Scale [mm]"), (9.012, 3.456))
    assert s2.attributes == {"Region Name": "bar",
                             "Energy Step": 0.5,
                             "Run Mode Information": {}}, \
        f"s2.attributes = {s2.attributes}."
    assert np.allclose(s2.data, [[5, 6], [7, 8]])


def test_read_3d():
    # expected interface
    spectra = read("data/scienta3D.txt")
    # test the right number of spectra were read
    assert len(spectra) == 1, "Expected on spectra collection."
    #
    s1, = spectra
    assert s1.axis("Binding Energy [eV]") == 0
    assert s1.axis(1) == 0, "1-index to 0-index broken."
    assert np.allclose(s1.scale("Binding Energy [eV]"), (624, 625, 626, 627)), \
        f"Binding energies don't match: {s1.scale('Binding Energy [eV]')}"
    assert s1.axis("Y-Scale [mm]") == 1
    assert s1.axis(2) == 1, "1-index to 0-index broken."
    assert np.allclose(s1.scale("Y-Scale [mm]"), (1.234, 5.678, 9.012))
    assert s1.axis("Seq. Iteration[a.u.]") == 2
    assert s1.axis(3) == 2, "1-index to 0-index broken."
    assert np.allclose(s1.scale("Seq. Iteration[a.u.]"), (1, 2))
    assert s1.attributes == {
            "Region Name": "foo",
            "Energy Step": 1,
            "Run Mode Information": {'Name': 'Add Dimension'}}, \
        f"s1.attributes = {s1.attributes}."
    assert np.allclose(s1.data,
        [[[ 1, 13],
          [ 2, 14],
          [ 3, 15]],
         [[ 4, 16],
          [ 5, 17],
          [ 6, 18]],
         [[ 7, 19],
          [ 8, 20],
          [ 9, 21]],
         [[10, 22],
          [11, 23],
          [12, 24]]])
