import biobabel
import numpy as np
import os
import datetime


import pyxdf  # pip3 install pyxdf
from scipy.interpolate import interp1d




def load(fname):
    """Load LSL format XDF file."""

    bio = biobabel.Biodata()  # create a new biodata object
    bio.name = fname

    # This file is included in bioread
    streams, header = pyxdf.load_xdf(fname,
                                     dejitter_timestamps=True, # should be default, but just to be sure
                                     synchronize_clocks=True
                                     )
    #print(header)


    
    participants = [ stringify(s["info"]["name"]) for s in streams]
    participants.sort()
    bio.participants = participants

    # Determine the common time onset of signals, so that we can then crop to that.
    ONSET_T, OFFSET_T = get_onset_offset(streams)

    for s in streams:
        info = s["info"] # Fetch metadata about this stream
        stream_name = stringify(info["name"])
        stream_type = stringify(info["type"]).lower()
        
        #print("Reading stream {} {}".format(stream_name,stream_type))
        dtype = stringify(info['channel_format'])
        if dtype=='string':
            continue # work with strings later # TODO

        modality = biobabel.guess_modality(stream_type)
        
        # Find out which time stamps are within the time range
        rawdata = s["time_series"].T[0]
        # just take the first stream # TODO: This could be expanded to extract multiple streams
        timestamps = s['time_stamps']

        SR = info['effective_srate'] # take the effective sampling rate since the nominal can be off or even zero
        
        # Use interpolation to get a regular sampled grid determined by the effective sampling rate
        target_t = np.arange(ONSET_T,np.max(timestamps),1/SR)
        f = interp1d(timestamps, rawdata, kind='nearest', bounds_error = False, fill_value=np.nan)
        signal_interp = f(target_t)
        
        #SR = float(info["nominal_srate"][0])  # info['effective_srate']
        units = 'unknown'
        desc = info.get('desc',[])
        if desc and desc[0]:
            units = desc[0]["channels"][0]["channel"][0]["unit"][0]

        hdr = {
            "id": stream_name,
            "participant": stream_name,
            "sampling_frequency": SR,
            "modality": modality,
            "units": units,
        }
        dat = signal_interp
        bio.add_channel((hdr, np.array(dat)))

    if 'datetime' in header['info']:
        bio.meta["date"] = stringify(header["info"]["datetime"])

    return bio







def get_onset_offset(streams):
    """
    One issue is that in XDF, streams can start at different moments in time.
    Here we need to align them all to a common offset.
    The idea is to find the earliest moment in time any one stream starts.
    Later, when we resample the data, we can simply set the streams to NA
    before that. 
    """

    start_ts = [min(s["time_stamps"]) for s in streams]
    ONSET_T = min(start_ts)

    end_ts = [max(s["time_stamps"]) for s in streams]
    OFFSET_T = max(end_ts)
    
    #n_samp = [sum(s["time_stamps"] >= ONSET_T) for s in streams]
    #print(n_samp)
    #N_SAMP = min(n_samp)  # take the smallest common time portion

    return ONSET_T, OFFSET_T







def stringify(vals):
    """
    pyxdf tends to supply parameter values as 1-item arrays for some reason.
    e.g.
    'name': ['SendDataC'],
    'type': ['EEG']
    
    Biobabel doesn't use that system, so here, to avoid throwing away data,
    let's concatenate the strings into a single value.
    """
    return " ".join([ str(s) for s in vals])


