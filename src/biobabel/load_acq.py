

# Input data from our own flavour of HDF5-dataset

import biobabel
import numpy as np
import os
import datetime

import bioread


def load(fname):

    """ Load BioPAC acq file """
    
    bio = biobabel.Biodata() # create a new biodata object

    # This file is included in bioread
    data = bioread.read_file(fname)
    
    bio.name = fname
    earliest = data.earliest_marker_created_at
    if earliest:
        dt       = earliest.strftime(biobabel.DATEFORMAT)#"%m/%d/%Y %H:%M:%S %Z%z")
        bio.date = dt
    else:
        m_time = os.path.getmtime(fname)
        dt_m = datetime.datetime.fromtimestamp(m_time)
        bio.meta['date']=dt_m.strftime(biobabel.DATEFORMAT)
        

    for ch in data.channels:

        #print(" {}".format(ch.name))

        hdr = {
            'id'                :ch.name,
            'participant'       :'participant',
            'sampling_frequency':ch.samples_per_second,
            'modality'          :ch.name.split(' ')[0].lower(),
            'units'             :ch.units
        }
        dat = ch.data
        bio.add_channel((hdr,np.array(dat)))
    
    bio.markers = {}
    for m in data.event_markers:
        tp = str(m.type)
        idx = m.sample_index
        t = idx/ch.samples_per_second
        bio.markers[tp] = bio.markers.get(tp,[]) + [t] # Append the marker

    #bio.markers = {}
    #for m in hf.attrs.get('markers',[]):
    #    bio.markers[m] = hf.attrs[m][:] # get the markers in question, make a copy

    return bio
