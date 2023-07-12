

# Input data from our own flavour of HDF5-dataset

import biobabel
import numpy as np
import os
import datetime

from opensignalsreader import OpenSignalsReader



def load(fname):

    """ Load BioPAC acq file """
    
    bio = biobabel.Biodata() # create a new biodata object


    # Read OpenSignals file
    acq = OpenSignalsReader(fname)

    for k in acq.info:
        bio.add_meta(k,acq.info[k])
    
    SR = acq.sampling_rate

    bio.name = fname
    bio.date = acq.info['date']+' '+acq.info['time']

    for ch,label in zip(acq.channels,acq.labels):

        # ch is the channnel number, label is the corresponding label
        
        units = acq.units.get(label,'n/a')
        ran   = acq.ranges.get(label,'n/a')
        
        hdr = {
            'id'                :label,
            'participant'       :'participant',
            'sampling_frequency':SR,
            'modality'          :label,
            'units'             :units
        }
        dat = acq.signal(ch)
        bio.add_channel((hdr,np.array(dat)))
    
    return bio
