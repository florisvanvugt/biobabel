
import biobabel
import numpy as np
import os
import datetime


import pyxdf # pip3 install pyxdf


def load(fname):

    """ Load LSL format XDF file. """
    
    print("ATTENTION, this is a very case-specific script. Should not be used")
    print("in general to read XDF files.")
    print("Make sure you know what you are doing if you proceed here.")

    
    bio = biobabel.Biodata() # create a new biodata object
    bio.name = fname

    # This file is included in bioread
    streams, header = pyxdf.load_xdf(fname)
    print(header)

    participants = [ s['info']['name'][0] for s in streams ]
    participants.sort()
    bio.participants = participants

    # Determine the common onset 
    ONSET_T, N_SAMP = get_onset(streams)

    
    for s in streams:
        info = s['info']
        print(" {} {}".format(info['name'][0],info['type'][0]))
        tp = info['type'][0].lower()
        #if tp!='ecg': continue # for now we only accept ECG signals

        modality = tp
        p = info['name'][0]

        t_sel = s['time_stamps']>ONSET_T
        rawdata = s["time_series"].T[0][t_sel] # just take the first stream, and only after the common starting point
        rawdata = rawdata[:N_SAMP] # take only the common chunk
        sz = rawdata.shape[0]
        assert sz==N_SAMP

        SR = float(info['nominal_srate'][0]) #info['effective_srate']
        units = info['desc'][0]['channels'][0]['channel'][0]['unit'][0]

        hdr = {'id'                :p,
               'participant'       :p,
               'sampling_frequency':SR,
               'modality'          :modality,
               'units'             :units
               }
        dat = rawdata
        bio.add_channel((hdr,np.array(dat)))


    bio.meta['date']=header['info']['datetime'][0]
    
    return bio



def get_onset(streams):
    """
    One issue is that in XDF, streams can start at different moments in time.
    Here we need to align them all to a common offset.
    The idea is to find the earliest moment in time where all streams have started,
    and then cut off anything in any stream before that.
    It throws away some data (downside) but allows us to have everything
    aligned in time (upside).
    """

    start_ts = [ min(s['time_stamps']) for s in streams ]
    ONSET_T = max(start_ts)

    n_samp = [ sum(s['time_stamps']>=ONSET_T) for s in streams ]
    print(n_samp)
    N_SAMP = min(n_samp) # take the smallest common time portion

    print("---------- TIMING ----------")
    print("Joint start t={}".format(ONSET_T))
    print("Stream onset deltas (should not be too great)")
    print([ t-ONSET_T for t in start_ts ])
    print("Largest common duration: {} samples".format(N_SAMP))
    print("Duration mismatches (proportion of common duration)")
    print(" ".join([ "{:.4f}".format(n/N_SAMP) for n in n_samp ]))
    print()

    print("---------- SAMPLING RATES ----------")
    nominal_sr = [ float(s['info']['nominal_srate'][0]) for s in streams ]
    eff_sr     = [ float(s['info']['effective_srate']) for s in streams ]
    print("Nominal sampling rates:")
    print(" ".join([ "{:.2f}".format(n) for n in nominal_sr ]))
    print("Effective sampling rates:")
    print(" ".join([ "{:.2f}".format(n) for n in eff_sr ]))
    print()

    return ONSET_T,N_SAMP
