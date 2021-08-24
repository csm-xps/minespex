"""
XPS spectra are collected from numerous individual measurements (spectrum).
"""


import numpy as np
from abc import ABC, abstractmethod
from collections.abc import Hashable
from copy import deepcopy


class Spectra(ABC):
    """Abstract base class for spectra objects.
    """
    class Dimension(Hashable):
        def __init__(self, axis, name, scale):
            """Information about a dimension in the Spectra.

            Spectra contain information in dense blocks. Information about the
            dimension is capture in this helper class.

            Attributes:
                axis (int): (Immutable) Accessed through a property.
                name (str): (Immutable) Name of this property.
                size (int): (Immutable) Length (number of entries) in this
                    dimension.
                scale (tuple): (Immutable) Scale along this dimension. This
                    will generally be a tuple of floats.

            Args:
                axis (int): The axis index. Whether 0- or 1-indexed will depend
                    on the source data.
                name (str): Name for this dimension/axis.
                scale (array-like): Values/labels of this dimension. For
                    example, the binding energies at each step.
            """
            super().__init__()
            self.__axis = int(axis)
            self.__name = str(name)
            self.__scale = tuple(scale)

        def __hash__(self):
            return hash(self.axis) + hash(self.name) + hash(self.scale)

        def __str__(self):
            return f"Dimension {self.axis} ({self.name}): {self.scale}"

        @property
        def axis(self):
            return self.__axis

        @property
        def name(self):
            return self.__name

        @property
        def size(self):
            return len(self.__scale)

        @property
        def scale(self):
            return self.__scale

    def __init__(self, name=''):
        """Stores XPS data in a numpy.ndarray `Spectra.data`.

        Information about the dimensions--name, scale, and which axis--is
        accessible by name or index.

        Attributes:
            name (str): Name of this spectra.
            attributes (dict): Named attributes; the metadata associated with
                this spectra.
            data (numpy.ndarray): 2- or 3-D spectral data, e.g. intensities.
                Information about the dimensions (scale, name, etc.) is
                provided in the `dim` attribute.
            dim (Spectra.Dimension): Information about each dimension of the
                spectra.

        Args:
            name (str): Name of the Spectra.
        """
        self.name = name
        self.attributes = dict()
        self.dim = dict()
        self.data = np.array([])

    def get_dim(self, key):
        """Get the dimension corresponding to `key`.

        Args:
            key (int, str, tuple, or Spectra.Dimension): Key identifying the
                axis.

        Returns:
            Spectra.Dimension:
                The dimension information.
        """
        return self.dim.get(key, None)

    def set_dim(self, axis, name=None, scale=None):
        """Set dimension information.

        Set dimension information for the specified axis.

        Args:
            axis (int or Spectra.Dimension): The axis that is to be added.
            name (str): (optional) The name of the dimension to be added.
            scale (tuple): (optional) The scale/labels of the axis.

        Returns:
            None.
        """
        if isinstance(axis, Spectra.Dimension):
            dim = axis
            axis, name, scale = axis.axis, axis.name, axis.scale
        else:
            dim = Spectra.Dimension(axis=axis, name=name, scale=scale)
        self.rm_dim(axis)
        self.dim[dim] = dim
        self.dim[name] = dim
        self.dim[axis] = dim
        self.dim[scale] = dim

    def rm_dim(self, key):
        """Remove all references to the dimension identified by `key`.

        Args:
            key (int, str, tuple, or Spectra.Dimension): The axis to be removed.

        Returns:
            None.
        """
        dim = self.get_dim(key)
        if dim:
            axis, name, scale = dim.axis, dim.name, dim.scale
            if dim in self.dim:
                del self.dim[dim]
            if axis in self.dim:
                del self.dim[axis]
            if name in self.dim:
                del self.dim[name]
            if scale in self.dim:
                del self.dim[scale]

    @abstractmethod
    def axis(self, key):
        """Returns the axis of the dimension identified by `key`.

        While the data may be 1-indexed in the file, the return value from this
        function will be adjusted to be 0-indexed; that is, `Spectra.axis(1)`
        will return 0.

        Args:
            key (int, str, or Spectra.Dimension): Representation of the
                dimension whose axis is to be returned.

        Returns:
            int:
                Python-indexable axis of the requested axis, or None if not
                found. This method must be overloaded based on whether the
                source data is one-indexed or zero-indexed.
        """
        raise NotImplementedError("Axis depends on indexing convention of "
                                  "input file.")

    def name(self, key):
        """Returns the name of the dimension identified by `key`.

        Args:
            key (int, str, Spectra.Dimension): Representation of the dimension
                whose name is to be returned.

        Returns:
            str:
                Name of the requested axis, or None if not found.
        """
        try:
            return self.dim[key].name
        except KeyError:
            return None

    def scale(self, key):
        """Returns the scale of the dimension identified by `key`.

        Args:
            key (int, str, or Spectra.Dimension): Representation of the
                dimension whose scale is to be returned.

        Returns:
            numpy.ndarray:
                Scale of the requested axis, or None if not found.
        """
        try:
            return np.array(self.dim[key].scale)
        except KeyError:
            return None

    def size(self, key):
        """Returns the size (length) of the dimension identified by `key`.

        Args:
            key (int, str, or Spectra.Dimension): Representation of the
                dimension whose length is to be returned.

        Returns:
            int:
                Length along the requested axis.
        """
        try:
            return self.dim[key].size
        except KeyError:
            return None

    def integrate_along(self, key):
        """Integrates the spectra along the dimension identified by `key`.

        Args:
            key (int, str, or Spectra.Dimension): Representation of the
                dimension whose length is to be returned.

        Returns:
            Spectra:
                Spectra integrated along the specified axis, or the unchanged
                spectra if the axis is not found.
        """
        if key not in self.dim:
            return self
        # return value
        rval = type(self)(self.name)
        rval.attributes = deepcopy(self.attributes)
        # calculate the integrated spectra
        axis, scale = self.axis(key), self.scale(key)
        rval.data = np.trapz(self.data, x=scale, axis=axis)
        rval.data /= np.sum(scale[1:] - scale[:-1])
        # populate the dimension information.
        rmdim = self.get_dim(key)
        for dim in set(self.dim.values()):
            # drop the dimension that was reduced
            if dim is rmdim:
                continue
            # get the axis, name and scle of the dimension
            axis, name, scale = dim.axis, dim.name, dim.scale
            if axis > rmdim.axis:
                # the dimensionality has been reduced by 1.
                axis -= 1
            rval.set_dim(axis=axis, name=name, scale=scale)
        # done
        return rval


class Scienta(Spectra):
    def axis(self, key):
        try:
            return self.dim[key].axis-1
        except KeyError:
            return None
    axis.__doc__ = Spectra.axis.__doc__

class VAMAS(Spectra):

    def axis(self, key):
        try:
            return self.dim[key].axis-1
        except KeyError:
            return None
    axis.__doc__ = Spectra.axis.__doc__

    def __init__(self, name, attributes, data):
        super().__init__(name=name)
        self.attributes=attributes
        self.data = data