from biobabel.io import load

from biobabel import *

from biobabel.biodata import Biodata



def display():
    # Launch ECG analysis
    import sys
    import os

    fname = None
    if len(sys.argv)>1:
        fname = sys.argv[1]
    else:

        filetypes = (
            ('HDF5 dataset', '*.hdf5'),
            ('All files', '*.*')
        )

        fname = fd.askopenfilename(
            title='Select your recording',
            initialdir='.',
            filetypes=filetypes)

    if not fname:
        print("You need to select a file. Exiting now.")
        sys.exit(-1)

    if not os.path.exists(fname):
        print("File {} does not seem to exist. Exiting now.".format(fname))
        sys.exit(-1)
        
    bio = load(fname)
    bio.print()
    bio.plot()
