
import biobabel
import numpy as np
import os
import datetime


import pyedflib



def load(fname):

    """ Load EDF file. """
    
    bio = biobabel.Biodata() # create a new biodata object
    bio.name = fname

    h = pyedflib.highlevel.read_edf_header(fname)

    # Fill in time stamp
    m_time = os.path.getmtime(fname)
    dt_m = datetime.datetime.fromtimestamp(m_time)
    dt = h.get('startdate',dt_m)
    bio.meta['date']=dt.strftime(biobabel.DATEFORMAT)
    for k in h: # copy over the header information
        if k not in ['SignalHeaders','channels']:
            bio.add_meta(k,str(h[k]))

    # Get participant identifier
    participant = h.get('patientcode','participant')

    # Get signal headers
    headers = h['SignalHeaders']    

    # Start reading data
    f = pyedflib.EdfReader(fname)
    n = f.signals_in_file
    signal_labels = f.getSignalLabels()
    
    assert n==len(headers)
    
    for i,head in enumerate(headers):

        SR = head['sample_rate']
        lab = signal_labels[i]
        hdr = {
            'id'                :lab,
            'participant'       :participant,
            'sampling_frequency':SR,
            'modality'          :biobabel.guess_modality(lab),
            'units'             :head.get('dimension','unknown')
        }
        dat = f.readSignal(i)
        bio.add_channel((hdr,np.array(dat)))
    
    return bio

