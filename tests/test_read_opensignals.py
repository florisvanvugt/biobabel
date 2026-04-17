import pytest
import requests
import biobabel as bb


def test_read_opensignals():
    bio = bb.load('tests/samples/SampleECG.txt')
    _,dat = bio.get('ECG')
    assert len(dat)==21 # there are 21 data points in this sample file.

    
