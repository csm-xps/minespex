.. _files:

==================
Config Files, Etc.
==================

Several files are used to capture and record information about the analysis
process, such as initial parameters for fitting and relative sensitivity
factors.


Initial fitting parameters
==========================

Fitting spectra can be a niggly process, being sensitive to initial conditions,
count times, incident intensity, incident wavelength, and many others.


CSV Seed file
-------------

The seed file captures the initial guess for fitting an expected set of peaks
in a spectrum.

+-------+----------------+---------------------------------------------+
| Order | Heading        | Description                                 |
+=======+================+=============================================+
|     1 | Regions        | Element, Shell, and peak ID. E.g. Pb 4f_1   |
+-------+----------------+---------------------------------------------+
|     2 | Center Init    | Initial guess for this peak position.       |
+-------+----------------+---------------------------------------------+
|     3 | Center Min     | Minimum position for this peak.             |
+-------+----------------+---------------------------------------------+
|     4 | Center Max     | Maximum position for this peak.             |
+-------+----------------+---------------------------------------------+
|     5 | Sigma Init     | Initial guess for the peak width.           |
+-------+----------------+---------------------------------------------+
|     6 | Sigma Min      | Minimum peak width.                         |
+-------+----------------+---------------------------------------------+
|     7 | Sigma Max      | Maximum peak width.                         |
+-------+----------------+---------------------------------------------+
|     8 | Amp Init       | Initial guess for the peak height.          |
+-------+----------------+---------------------------------------------+
|     9 | Amp Min        | Minimum peak height.                        |
+-------+----------------+---------------------------------------------+
|    10 | Amp Max        | Maximum peak height.                        |
+-------+----------------+---------------------------------------------+
|    11 | Total Time (m) |                                             |
+-------+----------------+---------------------------------------------+
|    12 | Gamma Init     |                                             |
+-------+----------------+---------------------------------------------+
|    13 | Gamma Min      |                                             |
+-------+----------------+---------------------------------------------+
|    14 | Gamma Max      |                                             |
+-------+----------------+---------------------------------------------+
|    15 | Skew Init      | Initial guess for the skewness of the peak. |
+-------+----------------+---------------------------------------------+
|    16 | Skew Min       | Minimum peak skewness.                      |
+-------+----------------+---------------------------------------------+
|    17 | Skew Max       | Maximum peak skewness.                      |
+-------+----------------+---------------------------------------------+


================
XPS Data Formats
================


Scienta SES
===========

Scienta provides a text-based data format capable of recording multiple
scans. `minespex` supports and has been tested on the following versions:

- 1.3.1
