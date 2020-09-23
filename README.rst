`minespex` is an application and high-level python library enabling
high-throughput, semi-automated analysis of X-ray photoemission spectroscopy
(XPS) data.

Description
===========

`minespex` aids in the aggregation and analysis of in situ XPS spectra.

A multistep analysis is performed on one or more spectra. For quantitative
atomic concentration estimated the user must supply an appropriate `relative sensitivity factors (RSF)`_
key value pairs with the elements included to be analyzed. Spectra form
collections that match a user-defined set of filters; e.g., time-resolved
spectra, blue laser, high quality. For example, an analysis of matching spectra
may include:

- Adjust spectra based on a calibration file.
- Compare two (or more) spectra.
- Plot a semi-continuum of data for a single core level or peak, e.g. I 3d 5/2.

Spectra are organized into measurements, measurements into samples, and samples
into projects.

Measurements expect a set of properties: intensity vs. binding energy, X-ray
power, end time for experiment. Additional measurement settings may be
specified as key-value pairs in the case of changing in situ conditions (e.g.
laser power, temperature, etc.). In addition to measurement-specific settings,
metadata is collected on the operator, the date and time when the measurement
was collected, machine make and model, fixed temperature or conditions and
sample description.

Samples are physical specimens from which measurements are made. Sample
information includes composition, geometry, surface roughness, and most
importantly the fill description of layers following the format::

    substrate/layer1/layer2/...

Additional information about the sample may be collected in key-value pairs.
In addition to sample-specific information, `minespex` connects individual
samples to their predecessors—that is, the specimen from which a sample was
produced.

`minespex` accepts the following XPS spectra formats:

- **txt**: Generated from `Scienta SES XPS software`_.
- **VAMAS**: VAMAS is a common format for the exchange of surface science
  data and suitable for XPS as well as AES, EDX, FABMS, ISS, SIMS, SNMS, UPS,
  and XRF data. See `VAMAS Surface chemical analysis standard data transfer format with skeleton decoding programs`_
  for a description of the file format. The VAMAS format is defined in
  `ISO 14976:1998 Surface chemical analysis -- Data transfer format`_.


.. _relative sensitivity factors (RSF): http://www.tscienceandtech.org.uk/CourseNotesTSTC2017.pdf
.. _Scienta SES XPS software: ftp://ftp.scienta.se/SES/docs/Manuals/SES/SES%20Software%20Manual%20v5_0.pdf
.. _VAMAS Surface chemical analysis standard data transfer format with skeleton decoding programs: https://onlinelibrary.wiley.com/doi/abs/10.1002/sia.740130202
.. _ISO 14976:1998 Surface chemical analysis -- Data transfer format: https://www.iso.org/standard/24269.html
