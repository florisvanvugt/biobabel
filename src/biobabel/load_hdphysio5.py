

# Input data from our own flavour of HDF5-dataset

import h5py
import numpy as np

import biobabel
import numpy as np
import os
import datetime



def load(fname):

    bio = biobabel.Biodata() # create a new biodata object

    hf = h5py.File(fname,'r')

    if 'name' in hf.attrs:
        bio.name = hf.attrs['name']
    else:
        bio.name = fname
    
    if 'date' in hf.attrs:
        bio.date = hf.attrs['date']    

    if 'participants' not in hf.attrs:
        print("# Error, missing participants attribute in the root.")
        
    participants = hf.attrs['participants']

    for p in participants:
        for ch in hf[p].keys():
            nm = "{}/{}".format(p,ch)
            dset = hf[p][ch]
            SR = dset.attrs['SR']
            mod = dset.attrs['modality']
            hdr = {'id'                :nm,
                   'participant'       :p,
                   'sampling_frequency':SR,
                   'modality'          :mod}
            dat = np.array(dset[:]) # convert into numpy array just to be sure
            bio.add_channel((hdr,dat))
            
    bio.markers = {}
    for m in hf.attrs.get('markers',[]):
        bio.markers[m] = hf.attrs[m][:] # get the markers in question, make a copy

    return bio
