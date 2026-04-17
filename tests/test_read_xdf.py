
import pytest
import biobabel as bb


def test_read_opensignals():
    bio = bb.load('tests/samples/five_ecgs.xdf')
    channels = [ hdr['id'] for hdr,_ in bio.find() ]
    assert len(channels)==5
    assert 'C2AA3623' in channels

    
