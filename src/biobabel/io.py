
import biobabel.load_teensyecg
import biobabel.load_hdphysio5
import biobabel.load_lsl
import biobabel.load_acq
import biobabel.load_opensignals

import os


def load(fname,dialect=None):
    """
    Load physiology signal file.

    fname : filename of the file to be read
    dialect : the file format. If None, the format is guessed
    """
    
    if not os.path.exists(fname):
        print("File '{}' does not seem to exist.".format(fname))
        return
    
    if dialect==None:
        # Try to guess
        dialect = guess_dialect(fname)
        if dialect:
            print("Guessed that this is {} format.".format(dialect))
        
    if dialect=="teensyecg":
        return biobabel.load_teensyecg.load(fname)

    if dialect=="hdphysio5":
        return biobabel.load_hdphysio5.load(fname)

    if dialect=="lsl":
        return biobabel.load_lsl.load(fname)

    if dialect=="acq":
        return biobabel.load_acq.load(fname)

    if dialect=="opensignals":
        return biobabel.load_opensignals.load(fname)
    
    return None # did not manage to load





def guess_dialect(fname):

    if fname.lower().endswith('.hdf5'):
        return "hdphysio5" # guess
    if fname.lower().endswith('.xdf'):
        return "lsl" # guess
    if fname.lower().endswith('.acq'):
        return "acq" # guess

    if fname.lower().endswith('.txt'):

        # To guess the dialect, we have to actually probe the file itself
        with open(fname) as f:
            ln = f.readline()

        if ln.find('OpenSignals')>-1:
            return 'opensignals'

        return "teensyecg" # guess





                
