import sys
from typing import List
from minespex.base import spectra
import numpy as np


def vamas_from_file(filename:str):
    # Read in .vms file and input into dictionary

    vamas = {}

    with open(filename, 'r') as file:
        lines = map(lambda x: x.replace("\n", ""), file.readlines())

        (
            vamas["format"],
            vamas["institution"],
            vamas["instrument model"],
            vamas["operator"],
            vamas["experiment"],
            numCommentLines,
            *lines
        ) = lines

        numCommentLines = int(numCommentLines)
        commentLines, lines = (
            lines[:numCommentLines],
            lines[numCommentLines:]
        )
        vamas["comment"] = "\n".join(commentLines)

        (
            vamas["experiment mode"],
            vamas["scan mode"],
            *lines
        ) = lines

        if vamas["experiment mode"] == 'NORM' or vamas["experiment mode"] == 'SDP':
            (
                vamas["# of spectral regions"],
                *lines
            ) = lines

        elif vamas["experiment mode"] == 'MAP' or vamas["experiment mode"] == 'MAPDP':
            (
                vamas["# of spectral regions"],
                vamas["# of analysis positions"],
                vamas["# of discrete x coordinates"],
                vamas["# of discrete y coordinates"],
                *lines
            ) = lines

        (
            numExperimentVar,
            *lines
        ) = lines

        numExperimentVar = int(numExperimentVar)
        for var in range(numExperimentVar):
            (
                vamas[f'experimental variable label #{var + 1}'],
                vamas[f'experimental variable units #{var + 1}'],
                *lines
            ) = lines

        (
            numInclusionExclusion,
            numManualItems,
            numFutureUpgradeEx,
            numFutureUpgradeBlock,
            *lines
        ) = lines

        if int(numInclusionExclusion) != 0:
            sys.exit('Does not support parameter inclusion/exclusion')

        if int(numManualItems) + int(numFutureUpgradeEx) + int(numFutureUpgradeBlock) != 0:
            sys.exit('Manual/Future entries not supported')

        (
            vamas['# of blocks'],
            vamas['block id'],
            vamas['sample id'],
            year,
            month,
            day,
            hour,
            minute,
            second,
            _,
            numCommentLines,
            *lines
        ) = lines

        vamas['timestamp'] = f'{year}-{month}-{day} {hour}:{minute}:{second}'

        numCommentLines = int(numCommentLines)
        commentLines, lines = (
            lines[:numCommentLines],
            lines[numCommentLines:]
        )
        vamas["block comment"] = "\n".join(commentLines)

        (
            vamas['technique'],
            *lines
        ) = lines

        if vamas["experiment mode"] == 'MAP' or vamas["experiment mode"] == 'MAPDP':
            (
                vamas["x coordinate"],
                vamas["y coordinate"],
                *lines
            ) = lines

        for var in range(numExperimentVar):
            (
                vamas[f'experimental variable value #{var + 1}'],
                *lines
            ) = lines
        
        (
            vamas["analysis source label"],
            *lines
        ) = lines

        # SHORTCUT
        if (
            vamas["experiment mode"] in [
                "MAPDP",
                "MAPSVDP",
                "SDP",
                "SDPSV"
            ] or 
            vamas["technique"] in [
                "FABMS",
                "FABMS energy spec",
                "ISS",
                "SIMS",
                "SIMS energy spec",
                "SNMS",
                "SNMS energy spec"
            ]
        ):
            (
                vamas["sputtering ion/atom atomic #"],
                vamas["#of atoms in sputtering/atom particle"],
                vamas["sputtering ion/atom charge sign and number"],
                *lines
            ) = lines

        (
            vamas["analysis source characteristic energy"],
            vamas["analysis source strength"],
            vamas["analysis source beam width x"],
            vamas["analysis source beam width y"],
            *lines
        ) = lines

        if vamas["technique"] == 'XPS' or vamas["technique"] == 'XRF':
            vamas["analysis source units"] = 'watts'

        elif vamas["technique"] == 'FABMS' or vamas["technique"] == 'FABMS energy spec':
            vamas["analysis source units"] = 'beam equivalent'

        elif (
            vamas["technique"] in [
                'AES diff',
                'AES dir',
                'EDX',
                'ISS',
                'SIMS',
                'SIMS energy spec',
                'SNMS',
                'SNMS energy spec'
            ]
        ):
            vamas["analysis source units"] = 'nanoamps'

        if (
            vamas["experiment mode"] in [
                'MAP',
                'MAPDP',
                'MAPSV',
                'MAPSVDP',
                'SEM'
            ]
        ):
            (
                vamas["field of view x"],
                vamas["field of view y"],
                *lines
            ) = lines

        if (
            vamas["experiment mode"] in [
                'MAPSV',
                'MAPSVDP',
                'SEM'
            ]
        ):
            (
                vamas["first linescan start x coordinate"],
                vamas["first linescan start y coordinate"],
                vamas["first linescan finish x coordinate"],
                vamas["first linescan finish y coordinate"],
                vamas["last linescan finish x coordinate"],
                vamas["last linescan finish y coordinate"],
                *lines
            ) = lines

        (
            vamas["analysis source polar angle of incidence"],
            vamas["analysis source azimuth"],
            vamas["analyser mode"],
            vamas["analyser pas energy/retard ratio/mass resolution"],
            *lines
        ) = lines

        if vamas["technique"] == 'AES diff':
            (
                vamas["differential width"], 
                *lines
            ) = lines

        (
            vamas["magnfication of analyser transfer lens"],
            vamas["analyser work function/acceptance energy/ion"],
            vamas["target bias"],
            vamas["analysis width x"],
            vamas["analysis width y"],
            vamas["analyser axis take off polar angle"],
            vamas["analyser axis take off azimuth"],
            vamas["species label"],
            vamas["transition/change state label"],
            vamas["change of detected particle"],
            *lines
        ) = lines

        if vamas["scan mode"] == 'REGULAR':
            (
                vamas["abscissa label"],
                vamas["abscissa units"],
                vamas["abscissa start"],
                vamas["abscissa increment"],
                *lines
            ) = lines

        (
            numCorrespondingVar,
            *lines
        ) = lines

        for var in range(int(numCorrespondingVar)):
            (
                vamas[f'Corresponding variable label #{var + 1}'],
                vamas[f'Corresponding variable units #{var + 1}'],
                *lines
            ) = lines

        (
            vamas["signal mode"],
            vamas["signal collection time"],
            vamas["# of scans to compile this block"],
            vamas["signal time correction"],
            *lines
        ) = lines

        if (
            vamas["technique"] in [
                'AES diff',
                'AES dir',
                'EDX',
                'ELS',
                'UPS',
                'XPS',
                'XRF'
            ] and
            vamas["experiment mode"] in [
                'MAPDP',
                'MAPSVDP',
                'SDP',
                'SDPSV'
            ]
        ):
            (
                vamas["sputtering source energy"],
                vamas["sputtering source beam current"],
                vamas["sputtering source width x"],
                vamas["sputtering source width y"],
                vamas["sputtering source polar angle of incidence"],
                vamas["sputtering source azimuth"],
                vamas["sputtering mode"],
                *lines
            ) = lines

        (
            vamas["sample normal polar angle of tilt"],
            vamas["sample normal azimuth angle of tilt"],
            vamas["sample rotation angle"],
            numAdditionalParamenter,
            *lines
        ) = lines

        for par in range(int(numAdditionalParamenter)):
            (
                vamas[f'additional parameter label #{par + 1}'],
                vamas[f'additional parameter units #{par + 1}'],
                vamas[f'additional parameter value #{par + 1}'],
                *lines
            ) = lines

        (
            vamas["# of ordinate values"],
            *lines
        ) = lines

        for var in range(int(numCorrespondingVar)):
            (
                vamas[f'minimum ordinate value #{var + 1}'],
                vamas[f'maximum ordinate value #{var + 1}'],
                *lines
            ) = lines

        for each in range(int(vamas["# of blocks"])):
            data = []
            (entry, *lines) = lines
            while entry != 'end of experiment':
                data.append(int(entry))
                (entry, *lines) = lines
            vamas[f'block #{each + 1} data'] = data

    return vamas

def vamas_to_spectra(vamas:dict):
    # Take VAMAS dictionary and return spectra class object

    blocksList =[]
    for key, value in vamas.items():

        if 'block #' in key:
            blocksList.append(key)

    keys = ['experiment']
    keys.extend(blocksList)

    # Take out keys for 'experiment' and block data because they are represented already
    attributes = {k:v for k,v in vamas.items() if k not in keys}

    data = []
    for block in blocksList:
        data.append(vamas[block])

    spectraVAMAS = spectra.VAMAS(name=vamas['experiment'],attributes=attributes, data=np.asarray(data))

    # Add dim data to fit spectra format
    start = int(vamas['abscissa start'])
    increment = float(vamas['abscissa increment'])
    numValues = float(vamas['# of ordinate values'])

    stop = int(start + (increment*(numValues-1)))
    scale = np.linspace(start, stop, int(numValues))
    scale = tuple(scale)
    spectraVAMAS.set_dim(axis=1, name=f'{vamas["abscissa label"]} ({vamas["abscissa units"]})', scale=scale)

    return spectraVAMAS

def read(filename: str):
    # Read in .vms file and output spectra class object

    vamasDict = vamas_from_file(filename)
    spectraVAMAS = vamas_to_spectra(vamasDict)
    return spectraVAMAS

