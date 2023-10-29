

# Input data from our own flavour of HDF5-dataset

import biobabel
import numpy as np
import os
import datetime

from pybdf import bdfRecording


def load(fname):

    """ Load BDF file """
    
    bio = biobabel.Biodata() # create a new biodata object

    # This file is included in bioread
    bdfRec = bdfRecording(fname)
    
    bio.name = fname
    m_time   = os.path.getmtime(fname)
    dt_m     = datetime.datetime.fromtimestamp(m_time)
    bio.date = dt_m.strftime(biobabel.DATEFORMAT)

    rec = bdfRec.getData()
    
    for i,ch in enumerate(rec['chanLabels']):
    
        hdr = {
            'id'                :ch,
            'participant'       :'participant',
            'sampling_frequency':bdfRec.sampRate[i],
            'modality'          :ch.lower(),
            'units'             :ch.lower()
        }
        dat = rec['data'][i]
        bio.add_channel((hdr,np.array(dat)))

    # TODO: process event markers
    #for m in data.event_markers:
    #    print('unprocessed marker {0}: Channel {1}, type {2}'.format(m.text, m.channel_name, m.type))

    #bio.markers = {}
    #for m in hf.attrs.get('markers',[]):
    #    bio.markers[m] = hf.attrs[m][:] # get the markers in question, make a copy

    return bio
