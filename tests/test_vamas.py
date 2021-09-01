import pytest
import numpy as np
from numpy.core.numeric import allclose
from minespex.io import vamas, scienta

@pytest.fixture
def input_filename():
    return "data/vamas.vms"


@pytest.fixture
def vamas_output():
    return "data/vamas-out.vms"


@pytest.fixture
def scienta_output():
    return "data/scienta-out.txt"


def test_read(input_filename):
    vamasSpectra = vamas.read(input_filename)

    assert vamasSpectra.name == "O1s_Sect_Sect", "Incorrect name"
    assert int(vamasSpectra.attributes['# of ordinate values']) == int(vamasSpectra.size(1))
    assert int(vamasSpectra.attributes['# of ordinate values']) == 111, "Incorrect size of data"
    assert vamasSpectra.dim[1].name == "Binding Energy [eV]"
    assert vamasSpectra.attributes['signal mode'] == 'pulse counting'
    assert vamasSpectra.attributes['# of blocks'] == '1'


    # Assert data is present and correct
    assert allclose(
        vamasSpectra.data,
        [[
            50811.5,
            49890.7,
            50722.7,
            49579,
            50286.7,
            49569.9,
            50965.6,
            50201.4,
            50104.3,
            49256.4,
            50101.5,
            49149.9,
            49156,
            50778.2,
            50743.6,
            49690.3,
            49430.8,
            50288.6,
            49218.3,
            51116.7,
            50783.6,
            51698.2,
            50083.7,
            51738,
            51782.4,
            50769.5,
            50619.5,
            51450.2,
            49592.4,
            51379.7,
            51192.5,
            50209.7,
            50496.5,
            51509.3,
            51425.2,
            51834,
            51836.7,
            50800.3,
            51171.9,
            51983,
            53368.1,
            52173.5,
            52542.4,
            52495,
            52867.6,
            54092.8,
            53860.2,
            55679.6,
            54917.1,
            56310.7,
            56669.3,
            58771.3,
            57258,
            59305.1,
            62279.5,
            61765.6,
            63121.4,
            63857,
            64059,
            64200.1,
            66706,
            65719.5,
            65634,
            68268,
            68845.7,
            68883.9,
            68274.6,
            69370.3,
            68772.4,
            69159.7,
            68368.6,
            67333.5,
            66265.2,
            65364.1,
            63806.1,
            62697,
            60821.7,
            58508.6,
            58441.3,
            57858.7,
            55729.8,
            53337.8,
            53746.6,
            52456.6,
            50515.3,
            51018.1,
            52499.4,
            51689.8,
            50367.3,
            51123.7,
            51067.2,
            50497.9,
            51650.5,
            50454.4,
            50995.2,
            50480,
            47931.4,
            49588.7,
            50969.7,
            51995.9,
            51265.9,
            49537.8,
            50362.8,
            49141.7,
            49967.6,
            50030.8,
            50030.1,
            50294.9,
            50264.7,
            49764.1,
            51161.9
        ]])


def test_write(input_filename, vamas_output, scienta_output):
    spectraVamas = vamas.read(input_filename)
    print(spectraVamas.attributes)
    vamas.write_to_vamas(spectraVamas, vamas_output)
    scienta.write_to_scienta(spectraVamas, scienta_output)
    return spectraVamas
