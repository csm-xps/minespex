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
            vamas["analyser pass energy/retard ratio/mass resolution"],
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
                vamas[f'corresponding variable label #{var + 1}'],
                vamas[f'corresponding variable units #{var + 1}'],
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

        ######
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
                data.append(float(entry))
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
    spectraVAMAS.set_dim(axis=1, name=f'{vamas["abscissa label"]} [{vamas["abscissa units"]}]', scale=scale)

    return spectraVAMAS

def read(filename: str):
    # Read in .vms file and output spectra class object

    vamasDict = vamas_from_file(filename)
    spectraVAMAS = vamas_to_spectra(vamasDict)
    return spectraVAMAS

def write_to_vamas(spectraObj: spectra.VAMAS or spectra.Scienta, filename:str, foldername:str = '', overwriteFile:bool = False):
    if overwriteFile:
        writeFile = 'w'
    else:
        writeFile = 'x'

    if foldername != '':
        foldername = f'{foldername}/'
    
    fileFormatList =[]

    if isinstance(spectraObj, spectra.VAMAS):

        tempList= [
            spectraObj.attributes["format"],
            spectraObj.attributes["institution"],
            spectraObj.attributes["instrument model"],
            spectraObj.attributes["operator"],
            spectraObj.name]

        if spectraObj.attributes['comment'] != '':
            tempList.append(1)
            tempList.append(spectraObj.attributes['comment'])
        else:
            tempList.append(0)

        tempList.append(spectraObj.attributes["experiment mode"])
        tempList.append(spectraObj.attributes["scan mode"])
        fileFormatList.extend(tempList)

        if "# of spectral regions" in spectraObj.attributes.keys():
            fileFormatList.append(spectraObj.attributes["# of spectral regions"])

            if "# of analysis positions" in spectraObj.attributes.keys():
                tempList = [
                    spectraObj.attributes["# of analysis positions"],
                    spectraObj.attributes["# of discrete x coordinates"],
                    spectraObj.attributes["# of discrete y coordinates"]]
                fileFormatList.extend(tempList)

        experimentVarCount = 1
        experimentVarBool = f'experimental variable label #{experimentVarCount}' in spectraObj.attributes.keys()
        tempList =[]
        experimentVarValue = []
        while experimentVarBool:
            tempList.append(spectraObj.attributes[f'experimental variable label #{experimentVarCount}'])
            tempList.append(spectraObj.attributes[f'experimental variable units #{experimentVarCount}'])
            experimentVarValue.append(spectraObj.attributes[f'experimental variable value #{experimentVarCount}'])
            experimentVarCount = experimentVarCount + 1
            experimentVarBool = f'experimental variable label #{experimentVarCount}' in spectraObj.attributes.keys()
        fileFormatList.append(experimentVarCount-1)
        fileFormatList.extend(tempList)

        # Unsupported features
        tempList = [0,0,0,0]
        fileFormatList.extend(tempList)

        tempList = [
            spectraObj.attributes['# of blocks'],
            spectraObj.attributes['block id'],
            spectraObj.attributes['sample id']]
        fileFormatList.extend(tempList)

        #Take apart timestamp
        date, time = spectraObj.attributes['timestamp'].split(' ')
        year, month, day = date.split('-')
        hour, min, sec = time.split(':')
        millsec = 0

        tempList = [
            year,
            month,
            day,
            hour,
            min,
            sec,
            millsec
        ]
        fileFormatList.extend(tempList)

        if spectraObj.attributes["block comment"] != '':
            fileFormatList.append(1)
            fileFormatList.append(spectraObj.attributes['block comment'])
        else:
            fileFormatList.append(0)

        fileFormatList.append(spectraObj.attributes['technique'])

        if "x coordinate" in spectraObj.attributes.keys():
            fileFormatList.append(spectraObj.attributes['x coordinate'])
            fileFormatList.append(spectraObj.attributes['y coordinate'])

        fileFormatList.extend(experimentVarValue)
        fileFormatList.append(spectraObj.attributes['analysis source label'])

        if 'sputtering ion/atom atomic #' in spectraObj.attributes.keys():
            fileFormatList.append(spectraObj.attributes["sputtering ion/atom atomic #"])
            fileFormatList.append(spectraObj.attributes["#of atoms in sputtering/atom particle"])
            fileFormatList.append(spectraObj.attributes["sputtering ion/atom charge sign and number"])

        tempList = [
            spectraObj.attributes["analysis source characteristic energy"],
            spectraObj.attributes["analysis source strength"],
            spectraObj.attributes["analysis source beam width x"],
            spectraObj.attributes["analysis source beam width y"]
        ]
        fileFormatList.extend(tempList)

        if 'field of view x' in spectraObj.attributes.keys():
            fileFormatList.append(spectraObj.attributes['field of view x'])
            fileFormatList.append(spectraObj.attributes['field of view y'])

        if "first linescan start x coordinate" in spectraObj.attributes.keys():
            tempList = [
                spectraObj.attributes["first linescan start x coordinate"],
                spectraObj.attributes["first linescan start y coordinate"],
                spectraObj.attributes["first linescan finish x coordinate"],
                spectraObj.attributes["first linescan finish y coordinate"],
                spectraObj.attributes["last linescan finish x coordinate"],
                spectraObj.attributes["last linescan finish y coordinate"]
            ]
            fileFormatList.extend(tempList)

        tempList = [
            spectraObj.attributes["analysis source polar angle of incidence"],
            spectraObj.attributes["analysis source azimuth"],
            spectraObj.attributes["analyser mode"],
            spectraObj.attributes["analyser pass energy/retard ratio/mass resolution"]
        ]
        fileFormatList.extend(tempList)

        if 'differential width' in spectraObj.attributes.keys():
            fileFormatList.append(spectraObj.attributes['differential width'])

        tempList = [
            spectraObj.attributes["magnfication of analyser transfer lens"],
            spectraObj.attributes["analyser work function/acceptance energy/ion"],
            spectraObj.attributes["target bias"],
            spectraObj.attributes["analysis width x"],
            spectraObj.attributes["analysis width y"],
            spectraObj.attributes["analyser axis take off polar angle"],
            spectraObj.attributes["analyser axis take off azimuth"],
            spectraObj.attributes["species label"],
            spectraObj.attributes["transition/change state label"],
            spectraObj.attributes["change of detected particle"]
        ]
        fileFormatList.extend(tempList)

        if 'abscissa label' in spectraObj.attributes.keys():
            tempList = [
                spectraObj.attributes["abscissa label"],
                spectraObj.attributes["abscissa units"],
                spectraObj.attributes["abscissa start"],
                spectraObj.attributes["abscissa increment"]
            ]
            fileFormatList.extend(tempList)

        correspondingVarCount = 1
        correspondingVarBool = f'corresponding variable label #{correspondingVarCount}' in spectraObj.attributes.keys()
        correspondingVarValues = []
        tempList =[]
        while correspondingVarBool:
            tempList.append(spectraObj.attributes[f'corresponding variable label #{correspondingVarCount}'])
            tempList.append(spectraObj.attributes[f'corresponding variable units #{correspondingVarCount}'])

            correspondingVarValues.append(spectraObj.attributes[f'minimum ordinate value #{correspondingVarCount}'])
            correspondingVarValues.append(spectraObj.attributes[f'maximum ordinate value #{correspondingVarCount}'])

            correspondingVarCount = correspondingVarCount + 1
            correspondingVarBool = f'corresponding variable label #{correspondingVarCount}' in spectraObj.attributes.keys()
        fileFormatList.append(correspondingVarCount-1)
        fileFormatList.extend(tempList)

        tempList = [
            spectraObj.attributes["signal mode"],
            spectraObj.attributes["signal collection time"],
            spectraObj.attributes["# of scans to compile this block"],
            spectraObj.attributes["signal time correction"]
        ]
        fileFormatList.extend(tempList)

        if "sputtering source energy" in spectraObj.attributes.keys():
            tempList = [
                spectraObj.attributes["sputtering source energy"],
                spectraObj.attributes["sputtering source beam current"],
                spectraObj.attributes["sputtering source width x"],
                spectraObj.attributes["sputtering source width y"],
                spectraObj.attributes["sputtering source polar angle of incidence"],
                spectraObj.attributes["sputtering source azimuth"],
                spectraObj.attributes["sputtering mode"]
            ]
            fileFormatList.extend(tempList)

        tempList = [
            spectraObj.attributes["sample normal polar angle of tilt"],
            spectraObj.attributes["sample normal azimuth angle of tilt"],
            spectraObj.attributes["sample rotation angle"],
        ]
        fileFormatList.extend(tempList)

        addParameterCount = 1
        addParameterBool = f'additional parameter label #{addParameterCount}' in spectraObj.attributes.keys()
        tempList =[]
        while addParameterBool:
            tempList.append(spectraObj.attributes[f'additional parameter label #{addParameterCount}'])
            tempList.append(spectraObj.attributes[f'additional parameter units #{addParameterCount}'])
            tempList.append(spectraObj.attributes[f'additional parameter value #{addParameterCount}'])

            addParameterCount = addParameterCount + 1
            addParameterBool = f'additional parameter label #{addParameterCount}' in spectraObj.attributes.keys()
        fileFormatList.append(addParameterCount-1)
        fileFormatList.extend(tempList)

        fileFormatList.append(spectraObj.attributes["# of ordinate values"])
        fileFormatList.extend(correspondingVarValues)

        for block in spectraObj.data:
            fileFormatList.extend(block)
            fileFormatList.append('end of experiment')

        with open(f'{foldername}{filename}.vms', writeFile) as file_out:
            write = file_out.write
            writeline = lambda line: file_out.write(f"{line}\n")
            [writeline(item) for item in fileFormatList]

    elif isinstance(spectraObj, spectra.Scienta):
        yLength = spectraObj.data.shape[1]
        timeStepLength = spectraObj.data.shape[2] if len(spectraObj.data.shape) == 3 else 1
        for yElement in range(yLength):
            for timeStep in range(timeStepLength):
                fileFormatList = []

                tempList =[
                    'VAMAS Surface Chemical Analysis Standard Data Transfer Format 1988 May 4',
                    spectraObj.attributes['Location'],
                    spectraObj.attributes['Instrument'],
                    spectraObj.attributes['User'],
                    f'{spectraObj.attributes["Region Name"]}-y{yElement}-{timeStep}',
                    1,
                    spectraObj.attributes['Comments'],
                    'Unknown',
                    'REGULAR',
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    spectraObj.attributes['Region Name'],
                    spectraObj.attributes['Sample']
                ]
                fileFormatList.extend(tempList)

                #Extracting date and time info
                year, month, day = spectraObj.attributes['Date'].split('-')
                hour, min,sec = spectraObj.attributes['Time'].split(':')
                millsec = 0

                tempList = [
                    year,
                    month,
                    day,
                    hour,
                    min,
                    sec,
                    millsec,
                    0,
                    'XPS',              #Assumption of use of XPS
                    spectraObj.attributes['Excitation Energy'],
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    'Unknown',
                    spectraObj.attributes['Pass Energy'],
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    spectraObj.attributes['Sample'],
                    '',
                    -1
                ]
                fileFormatList.extend(tempList)

                dimKeys = list(spectraObj.dim.keys())
                label, units =spectraObj.dim[dimKeys[0]].name.split(' [')
                units = units[:-1]
                start = float(spectraObj.dim[dimKeys[0]].scale[0])
                increment = start-float(spectraObj.dim[dimKeys[0]].scale[1])

                tempList = [
                    label,
                    units,
                    start,
                    increment,
                    0,
                    'Unknown',
                    float(spectraObj.attributes['Step Time'])/1000.0,
                    spectraObj.attributes['Number of Sweeps'],
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    '1e+37',
                    spectraObj.size(dimKeys[0])
                ]
                fileFormatList.extend(tempList)
                data = list(spectraObj.data[:,yElement,timeStep])
                fileFormatList.extend(data)


                with open(f'{foldername}{filename}-y{spectraObj.dim[dimKeys[0]].scale[yElement]}-{timeStep}.vms', writeFile) as file_out:
                    write = file_out.write
                    writeline = lambda line: file_out.write(f"{line}\n")
                    [writeline(item) for item in fileFormatList]
    

