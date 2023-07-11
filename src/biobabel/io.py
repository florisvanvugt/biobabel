
import biobabel.load_teensyecg
import biobabel.load_hdphysio5
import biobabel.load_lsl

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
        if fname.lower().endswith('.hdf5'):
            dialect="hdphysio5" # guess
        if fname.lower().endswith('.txt'):
            dialect="teensyecg" # guess
        if fname.lower().endswith('.xdf'):
            dialect="lsl" # guess

        if dialect:
            print("Guessed that this is {} format.".format(dialect))
            
    if dialect=="teensyecg":
        return biobabel.load_teensyecg.load(fname)

    if dialect=="hdphysio5":
        return biobabel.load_hdphysio5.load(fname)

    if dialect=="lsl":
        return biobabel.load_lsl.load(fname)
    
    return None # did not manage to load





