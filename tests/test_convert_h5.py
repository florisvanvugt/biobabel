
import biobabel
import os
import pathlib
import pytest


@pytest.fixture
def convert_opensignals_file(tmp_path):
    # before test - convert the sample ECG opensignals
    # file into the biobabel HDF5 format and save it.
    bio = biobabel.load('tests/samples/SampleECG.txt')
    target_output = os.path.join(tmp_path,'SampleECG.hdf5')
    bio.save(target_output)
    yield target_output
    # after test - remove resource
    #target_output.unlink()


def test_conversion_correct(convert_opensignals_file):

    bio = biobabel.load(convert_opensignals_file)
    channels = [ hdr['id'] for hdr,_ in bio.find() ]
    assert len(channels)==1

    
