# Test reading of BioPac acknowledge files

import biobabel as bb

def test_read():
    bio = bb.load('tests/samples/biopac_sample.acq')
    info,dat=bio.get('RSP, X, RSPEC-R')
    assert info['sampling_frequency']==2000.0
