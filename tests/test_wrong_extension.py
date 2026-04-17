# Test to see if an error is thrown when reading a file
# that has the wrong extension. 

import biobabel as bb
from pytest import approx
import pytest

ACQ_EDF_FILE = "tests/samples/biopac_sample_wrong_extension.edf"

def test_wrong_extension():
    # Here we read a file that is in the AcqKnowledge format,
    # but has been given the (erroneous) edf extension.
    # The desired behavior is to raise an exception.
    with pytest.raises(OSError):
        bio = bb.load(ACQ_EDF_FILE)



def test_override():
    # Here we specifically tell biobabel to read the file
    # as an acknowledge file.
    # The desired behavior is that biobabel should read the contents of the file
    bio =bb.load_acq.load(ACQ_EDF_FILE)
    _, dat = bio.get('PPG, X, PPGED-R')
    assert dat[1]==approx(0.36407470703125) # point check that data is read correctly
