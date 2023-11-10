from biobabel.io import load

from biobabel import *

from biobabel.biodata import Biodata

DATEFORMAT = "%Y/%m/%d %H:%M:%S %Z%z"


def display(viewer=False):

    import sys
    import os
    from tkinter import filedialog as fd

    fname = None
    if len(sys.argv)>1:
        fname = sys.argv[1]
    else:

        filetypes = (
            ('All files', '*.*'),
            ('HDF5 dataset', '*.hdf5')
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

    if viewer:
        import biobabel.viewer as viewer
        viewer.main(bio)

    else:
        #Simpler version:
        bio.plot()



def view():
    display(viewer=True)




def guess_modality(nm):
    """ Guess the modality from the label of a signal column """
    l = nm.lower()
    for mod in ['ecg','eda','gsr','ppg']:
        if l.find(mod)>-1:
            return mod
    return nm
    
