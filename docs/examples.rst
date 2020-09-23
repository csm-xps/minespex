.. _examples:

========
Examples
========

.. code-block:: python

    import os
    from TxtReaderV3 import data
    from XPS_Analysis import fit_routine, plotPb_0

    # user-defined settings
    input_filename = "/path/to/foo.txt" # Scienta XPS ver. 1.3.1
    seed_filename = "/path/to/seed.csv" # format described in "Data Formats"
    rsf = {'I 3d 5/2': 1.234, 'Pb 4f 1/2': 5.678}

    # ##### boilerplate ##### #
    # generate JSON output filename
    output_filename = os.path.splitext(os.path.basename(input_filename))[0] + '.json'
    # read the data
    data(input_filename) # generates output_filename in the current directory
    # fit the data
    fit_routine(output_filename, seed_filename, rsf)
    # plot the fitted data
    plotPb_0([output_filename, output_filename])
