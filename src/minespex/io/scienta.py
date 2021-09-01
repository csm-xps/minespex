"""Classes and functions to read Scienta-formatted data.
"""

from ..base.spectra import VAMAS, Scienta
from ..base.util import as_basic_type
from copy import deepcopy
from io import StringIO
import re
import numpy as np

import logging
_logger = logging.getLogger()


# debugging
import sys


class Reader:
    VERSIONS = ("1.3.1",)

    class BlockIter:
        class Block:
            def __init__(self):
                self.name = None
                self.index = None
                self.contents = []

        def __init__(self, fobj):
            """Block object to be read from `fobj`.

            Scienta-formatted input files are separated into regions, spectra
            collected for a specific element-electron level combination. The
            regions themselves are composed of blocks. These blocks are
            relatively simple. This class handles iteration through blocks.

            Example:
                Iterating through blocks::

                    with open("scienta_file.txt") as ifs:
                        for block in Reader.BlockIter(ifs):
                            print(f"Block name: {block.name}")
                            print(f"Block index: {block.index}")
                            print(f"Block contents: {block.contents}")

            Since the start of a new region is only determined when indicated
            by the next block, and thus by necessity, this next block must have
            already been read. Therefore, `BlockIter` must also have a means
            of rewinding one block. This is handled through the `BlockIter.prev`
            function.

            Example:
                Rewind to the previous block::

                    ifs = open("scienta_file.txt")
                    blockiter = Reader.BlockIter(ifs)
                    blockA = blockiter.next()
                    blockiter.prev()
                    blockB = blockiter.next()
                    # blockA and blockB both contains the contents of the first
                    # block in "scienta_file.txt".

            Args:
                fobj (file-like object): File stream from which the blocks to
                    be read.
            """
            # stream object from which the spectra are to be read.
            self.__fobj = fobj
            self._start = [0]

        def __iter__(self):
            return self

        def __next__(self):
            return self.next()

        def next(self):
            """Loads one block from a readable filestream-like object.

            Returns:
                Reader.BlockIter.Block:
                    The block read from the iterator's file object.
            """
            inblock = False
            block = None
            regex = re.compile(r'^\[([^0-9:]+)(?:\s+([0-9:]+))*\]')
            # rewind the stream to the beginning of the next block
            self.__fobj.seek(self._start[-1])
            # read the next block
            self._start.append(self._start[-1])
            for line in self.__fobj:
                # check for a header
                match = re.match(regex, line.strip())
                if match:
                    if not inblock:
                        inblock = True
                        # process header
                        block = Reader.BlockIter.Block()
                        block.name, block.index = match.groups()
                        _logger.info("Read block {name}, index {index}".format(
                            name=block.name, index=block.index))
                    else:
                        break
                else:
                    # add the line to the block contents (if not an empty line).
                    content = line.strip()
                    if content != '' and block is not None:
                        block.contents.append(content)
                # keep track of the length of lines have been read. tell does
                # not work when reading a file line-by-line.
                self._start[-1] += len(line)
            if block is None:
                raise StopIteration()
            return block

        def prev(self):
            """Prepare to reread the previous block.

            A subsequent call to "next" will reread the last block read.
            """
            pos = self._start.pop()


    class RegionIter:
        def __init__(self, fobj):
            self.__fobj = fobj
            self.blockiter = Reader.BlockIter(fobj)
            self.region = None

        def __iter__(self):
            return self

        def __next__(self):
            return self.next()

        def next(self):
            """Loads one region at a time.

            Returns:
                Spectra.Scienta:
                    A collection of spectra for an element/electron energy
                    level.
            """
            region = None
            inregion = False
            for block in self.blockiter:
                
                if block.name == "Region":
                    if not inregion:
                        inregion = True
                        region = self.region = Scienta()
                        self.process_region_block(block)
                    else:
                        self.blockiter.prev()
                        break
                {
                    "Region": self.process_region_block,
                    "Info": self.process_info_block,
                    "Run Mode Information": self.process_run_mode_information_block,
                    "Data": self.process_data_block
                }.get(block.name, lambda b: None)(block)
            if region is None:
                raise StopIteration()
            return region

        def process_region_block(self, block):
            """Extracts information from "Region" block.

            This sets the name of the region and information about the
            dimensions of the data. The data may be 2 or 3 dimensional. Based
            on the information on the dimensions, room is reserved for the data
            set.

            Args:
                block (Reader.BlockIter.Block): A block read from `Blocks`.

            Returns:
                None.
            """
            assert block.name == "Region"
            kv = dict()
            # iterate through the contents of the block.
            for line in block.contents:
                key, sep, value = line.partition("=")
                match = re.match(r'Dimension (\d+) (\w+)', key)
                if match:
                    # look for block contents that start with
                    # Dimension (#) [dimension key]=[dimension value]
                    i, k = match.groups()
                    i = int(i)
                    value = {
                        "name": lambda s: str(s),
                        "size": lambda s: int(s),
                        "scale": lambda s: tuple(float(x) for x in s.split())
                    }.get(k, as_basic_type)(value)
                    kv[i] = {**kv.get(i, {'axis': i}), **{k: value}}
                elif re.match(r'Region Name', key):
                    self.region.name = value
            for kwds in kv.values():
                self.region.set_dim(axis=kwds["axis"],
                                    name=kwds["name"],
                                    scale=kwds["scale"])
            # finally, create the arrays to store the data.
            shape = tuple(kv[i]["size"] for i in range(1, len(kv)+1))
            self.region.data = np.ndarray(shape, dtype=float)

        def process_info_block(self, block):
            """Extracts information from the Info block.

            There are two such blocks: the global [Info] block and the Region
            [Info (#)] block. These are stored as key-value pairs (dict).

            Args:
                block (Reader.BlockIter.Block): Info block to be processed.

            Returns:
                None.
            """
            assert block.name == "Info"
            contents = {k:as_basic_type(v)
                        for line in block.contents
                        for k,s,v in [line.partition('=')]}
            if block.index is None:
                # check the global Info block for version compatibility.
                if contents["Version"] not in Reader.VERSIONS:
                    _logger.info(f"{contents['Version']} is not a tested "
                                  "Scienta version.")
            else:
                # collect attributes
                self.region.attributes.update(contents)

        def process_run_mode_information_block(self, block):
            """Extracts information from the Run Mode Information block.

            This is added to the `Spectra.attributes` variable as "Run Mode
            Information".

            Args:
                block (Reader.BlockIter.Block): Block to be processed.

            Returns:
                None.
            """
            assert block.name == "Run Mode Information"
            contents = {k:as_basic_type(v)
                        for line in block.contents
                        for k,s,v in [line.partition('=')]}
            self.region.attributes["Run Mode Information"] = contents

        def process_data_block(self, block):
            """Extracts information from each data block.

            This can be 2 or 3 dimensional. If 2D, then `Blocks.index` will be
            a single integer. If 3D, then `Blocks.index` will be of the form
            "#:#".

            Args:
                block (Reader.BlockIter.Block): Block that contains
                    spectroscopy data.

            Returns:
                None.
            """
            assert block.name == "Data"
            ixy, s, iz = block.index.partition(':')
            data = np.array([[float(col) for col in row.split()[1:]]
                             for row in block.contents])
            if iz:
                # data is 3D
                iz = int(iz)-1
                self.region.data[:,:,iz] = data
            else:
                # data is 2D
                self.region.data = data


    @classmethod
    def load(cls, fileobj):
        """Loads Scienta-formatted data.

        Args:
            fileobj (file-like): File-like object from which to read the XPS
                data. Must support `seek` and iteration.

        Returns:
            list(Scienta): Scienta spectra (regions) read.
        """
        return list(Reader.RegionIter(fileobj))

    @classmethod
    def loads(cls, string):
        """Loads Scienta-formatted data.

        Args:
            string (str): String from which to read Scienta-formatted data.

        Returns:
            list(Scienta):
                Scienta spectra (regions) read.
        """
        with StringIO(string) as ifs:
            return cls.load(ifs)


def read(filename):
    """Reads a Scienta-formatted input file.

    Args:
        filename (str): Name of the file that is to be read.

    Returns:
        list(Scienta):
            Scienta spectra (regions) read from the file.
    """
    with open(filename, 'r') as ifs:
        return Reader.load(ifs)

def write_to_scienta(spectraObj: VAMAS or list, filename:str, overwriteFile:bool=False): # No extention to filename
    
    """ Take in a Spectra object and write to a Scienta file format

        Parameters:
            spectraObj (Spectra(VAMAS) or list(Spectra(Scienta))): Spectra object or a list of Spectra objects
            filename (str): Name of file to write to including extensions
            overwrite (bool): Argument to determine if files already existing should be overwritten.
                Defaults to False, meaning files will not be overwriten.

        Returns:
            None

    """
    
    if overwriteFile:
        writeFile = 'w'
    else:
        writeFile = 'x'
    
    if spectraObj == []:
        spectraObj.append(1)
    
    fileFormatList =[]
    
    if isinstance(spectraObj, list):
        if isinstance(spectraObj[0], Scienta):

            regions = len(spectraObj)
            tempList = [
                '[Info]',
                f'Number of Regions={regions}',
                'Version=Unknown',
                ''
            ]
            fileFormatList.extend(tempList)

            for numObj in range(len(spectraObj)):
                obj = spectraObj[numObj]

                fileFormatList.append(f'[Region {numObj+1}]')
                fileFormatList.append(f'Region Name={obj.attributes["Region Name"]}')

                numDim = len(obj.dim)/4
                for eachDim in range(int(numDim)):
                    scale = ''
                    for each in obj.dim[eachDim+1].scale:
                        scale = f'{scale} {each}'
                    scale = scale[1:]
                    tempList = [
                        f'Dimension {eachDim+1} name={obj.dim[eachDim+1].name}',
                        f'Dimension {eachDim+1} size={obj.dim[eachDim+1].size}',
                        f'Dimension {eachDim+1} scale={scale}'
                    ]
                    fileFormatList.extend(tempList)
                
                tempList = [
                    '',
                    f'[Info {numObj}]',
                    f'Region Name={obj.attributes["Region Name"]}',
                    f'Lens Mode={obj.attributes["Lens Mode"]}',
                    f'Pass Energy={obj.attributes["Pass Energy"]}',
                    f'Number of Sweeps={obj.attributes["Number of Sweeps"]}',
                    f'Excitation Energy={obj.attributes["Excitation Energy"]}',
                    f'Energy Scale={obj.attributes["Energy Scale"]}',
                    f'Acquisition Mode={obj.attributes["Acquisition Mode"]}',
                    f'Energy Unit={obj.attributes["Energy Unit"]}',
                    f'Center Energy={obj.attributes["Center Energy"]}',
                    f'Low Energy={obj.attributes["Low Energy"]}',
                    f'High Energy={obj.attributes["High Energy"]}',
                    f'Step Time={obj.attributes["Step Time"]}',
                    f'Detector First X-Channel={obj.attributes["Detector First X-Channel"]}',
                    f'Detector Last X-Channel={obj.attributes["Detector Last X-Channel"]}',
                    f'Detector First Y-Channel={obj.attributes["Detector First Y-Channel"]}',
                    f'Detector Last Y-Channel={obj.attributes["Detector Last Y-Channel"]}',
                    f'Number of Slices={obj.attributes["Number of Slices"]}',
                    f'File={obj.attributes["File"]}',
                    f'Sequence={obj.attributes["Sequence"]}',
                    f'Spectrum Name={obj.attributes["Spectrum Name"]}',
                    f'Instrument={obj.attributes["Instrument"]}',
                    f'Location={obj.attributes["Location"]}',
                    f'User={obj.attributes["User"]}',
                    f'Sample={obj.attributes["Sample"]}',
                    f'Comments={obj.attributes["Comments"]}',
                    f'Date={obj.attributes["Date"]}',
                    f'Time={obj.attributes["Time"]}',
                    f'Time per Spectrum Channel={obj.attributes["Time per Spectrum Channel"]}',
                    f'DetectorMode={obj.attributes["DetectorMode"]}',
                    f'[Run Mode Information {numObj+1}]',
                    f'Name={obj.attributes["Run Mode Information"]["Name"]}',
                    '',
                    '',
                    ''
                ]
                fileFormatList.extend(tempList)

                if numDim == 3:
                    for block in obj.dim[3].scale:
                        fileFormatList.append(f'[Data {numObj+1}:{int(block)}]')
                        for eachRow in range(len(obj.dim[1].scale)):
                            
                            row = f'{obj.dim[1].scale[eachRow]}' 
                            for eachCol in obj.data[eachRow,:,int(block-1)]:
                                row = f'{row} {eachCol}'
                            
                            fileFormatList.append(row)
                        fileFormatList.append('')

            with open(f'{filename}.txt', writeFile) as file_out:
                    write = file_out.write
                    writeline = lambda line: file_out.write(f"{line}\n")
                    [writeline(item) for item in fileFormatList]

            

        elif isinstance(spectraObj[0], VAMAS):
            print("VAMAS list")

    elif isinstance(spectraObj, VAMAS):
        print("VAMAS")

        scale = ''
        for each in spectraObj.dim[1].scale:
            scale = f'{scale} {each}'
        scale = scale[1:]

        tempList = [
                '[Info]',
                f'Number of Regions=1',
                'Version=Unknown',
                '',
                '[Region 1]',
                f'Region Name={spectraObj.attributes["species label"]}',
                f'Dimension 1 name={spectraObj.attributes["abscissa label"]} [{spectraObj.attributes["abscissa units"]}]',
                f'Dimension 1 size={spectraObj.attributes["# of ordinate values"]}',
                f'Dimension 1 scale={scale}',
                f'Dimension 2 name=Measurement',
                f'Dimension 2 size=1',
                f'Dimension 2 scale=0',
                '',
                '[Info 1]',
                f'Region Name={spectraObj.attributes["species label"]}',
                f'Lens Mode=Unknown',
                f'Pass Energy={spectraObj.attributes["analyser pass energy/retard ratio/mass resolution"]}',
                f'Number of Sweeps={spectraObj.attributes["# of scans to compile this block"]}',
                f'Excitation Energy={spectraObj.attributes["analysis source characteristic energy"]}',
                'Energy Scale=Unknown',
                'Acquisition Mode=Unknown',
                'Energy Unit=Unknown',
                'Center Energy=Unknown',
                'Low Energy=Unknown',
                'High Energy=Unknown',
                f'Energy Step={abs(float(spectraObj.attributes["abscissa increment"]))}',
                f'Step Time={float(spectraObj.attributes["signal collection time"])*1000}',
                'Detector First X-Channel=Unknown',
                'Detector Last X-Channel=Unknown',
                'Detector First Y-Channel=1',
                'Detector Last Y-Channel=1',
                f'Number of Slices=1',
                'File=Unknown',
                'Sequence=Unknown',
                f'Spectrum Name={spectraObj.attributes["species label"]}',
                f'Instrument={spectraObj.attributes["instrument model"]}',
                f'Location={spectraObj.attributes["institution"]}',
                f'User={spectraObj.attributes["operator"]}',
                f'Sample={spectraObj.attributes["sample id"]}',
                f'Comments={spectraObj.attributes["comment"]}'
            ]
        fileFormatList.extend(tempList)

        date, time = spectraObj.attributes["timestamp"].split(' ')
        tempList = [
            f'Date={date}',
            f'Time={time}',
            f'Time per Spectrum Channel=Unknown',
            f'DetectorMode=Unknown',
            '[Run Mode Information 1]',
            'Name=Unknown',
            '',
            '',
            '',
            '[Data 1]'
        ]
        fileFormatList.extend(tempList)

        for eachRow in range(len(spectraObj.dim[1].scale)):
            fileFormatList.append(f'{spectraObj.dim[1].scale[eachRow]} {spectraObj.data[0,eachRow]}')

        with open(f'{filename}.txt', writeFile) as file_out:
            write = file_out.write
            writeline = lambda line: file_out.write(f"{line}\n")
            [writeline(item) for item in fileFormatList]


