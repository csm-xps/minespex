"""Classes and functions to read Scienta-formatted data.
"""

from ..base.spectra import Scienta
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
                    if content != '':
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
