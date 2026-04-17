# Biobabel will by default guess the modality (type of data) in each channel of an
# input file. For instance, it will try to determine whether the data is
# ECG or PPG. 

import biobabel as bb
from pytest import approx
import pytest

H5_FILE = "tests/samples/example.hdf5"

def test_get_modality():
    # Here we read a file that is in the AcqKnowledge format,
    # but has been given the (erroneous) edf extension.
    # The desired behavior is to raise an exception.
    bio = bb.load(H5_FILE)
    hdr,_ = bio.get('a_ecg')
    assert hdr['modality']=='ecg'
    


def test_channel_update():
    # Suppose the modality of a channel is guessed wrong.
    # Here we use update_header() to correct the channel modality.
    bio = bb.load(H5_FILE)

    # Update the channel header
    bio.update_channel('b_ecg',{'modality':'eeg'}) # the channel modality to eeg
    hdr,_ = bio.get('b_ecg')
    assert hdr['modality']=='eeg' # not ecg anymore
    
