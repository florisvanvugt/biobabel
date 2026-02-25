# Test reading of BioPac acknowledge files

import biobabel as bb
from pytest import approx

def test_read():
    bio = bb.load("tests/samples/biopac_sample.acq")
    assert 'participant' in bio.get_participants()
    info, dat = bio.get("RSP, X, RSPEC-R")
    assert info["sampling_frequency"] == 2000.0
    assert dat[1]==approx(-0.31585693) # check one data point
    assert len(bio.find({'modality':'ppg'}))==2 # there should be two PPG channels
