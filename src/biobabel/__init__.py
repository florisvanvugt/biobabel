from biobabel.io import load

from biobabel import *

from biobabel.biodata import Biodata

DATEFORMAT = "%Y/%m/%d %H:%M:%S %Z%z"


def info():
    # Display info of a file
    get_file()


def get_file():
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
    bio.meta['filename']=fname
    return bio
    



def display(viewer=False):

    bio = get_file()

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
    






def split():
    """ Split a file according to its markers """
    bio = get_file() # attempt to get a file name to work on
    # If we're still here that means we have loaded a file

    # Extract all the markers, throw them on a big heap
    ts = []
    for m in bio.get_markers():
        ts += bio.get_marker(m)

    if 0 not in ts: ts.append(0)
    d = bio.get_duration()
    if d not in ts: ts.append(d)
    ts.sort()
    
    if len(ts)<3:
        print("Only {} time points (including beginning and ending). Not enough to split.")
        sys.exit(0)

    fname = bio.meta['filename']
    import os
    fbase,ext = os.path.splitext(fname)
        
    tprev = ts[0]
    for i,t in enumerate(ts):

        if abs(t-tprev)>0:
            targetf = "{}_{:03d}{}".format(fbase,i,'.hdf5')
            print("Cutting {} to {} => {}".format(tprev,t,targetf))
            # cut between tprev and t

            sub = bio.copy()
            sub.crop(tprev,t)
            sub.meta['filename']=targetf

            # Write file to hdf5 copy
            sub.save(targetf)
            
        tprev = t
    
