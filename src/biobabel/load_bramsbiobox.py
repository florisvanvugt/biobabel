
import biobabel
import numpy as np
import os
import datetime
import pandas as pd


col_info = {
    "Time(ms)": "t",
    "PPG": "ppg",
    "ECG": "ecg",
    "Gauge": "gauge",
    "Thermistor": "therm",
    "Xaccel": "xaccel",
    "Yaccel": "yaccel",
    "Zaccel": "zaccel"
}



def load(fname):

    """ Load a file with the BRAMS-Bio-Box format. """
    
    bio = biobabel.Biodata() # create a new biodata object
    bio.name = fname
    
    m_time = os.path.getmtime(fname)
    dt_m = datetime.datetime.fromtimestamp(m_time)
    bio.meta['date']=dt_m.strftime(biobabel.DATEFORMAT)

    ## gb['renames'] comes from the file configuration
    tab = pd.read_csv(fname,sep=',')

    TIME_DIVIDER = 1000

    tcol = 'Time(ms)'
    for col in tab.columns:
        if col.find(tcol)>-1:
            tcol = col
    tab[tcol]=tab[tcol]/TIME_DIVIDER  # express in s

    tdur = max(tab[tcol])-min(tab[tcol])
    dt = np.diff(tab[tcol])
    mediandt=np.median(dt)
    print("-- A human may want to inspect this:")
    print("Time step values (in s) min={:.5f}, max={:.5f}, mean={:.5f}, median={:.5f}, SD={:.5f}".format(
        np.min(dt),np.max(dt),np.mean(dt),mediandt,np.std(dt)))
    THRESH = mediandt*1.2
    nover,overprop = np.sum(dt>THRESH),np.mean(dt>THRESH)
    print("# of time steps > {}: {} ({:.4f} %)".format(THRESH,nover,overprop*100))
    print("----")
    print()

    SR = 1/mediandt

    participant = 'participant'

    for col in tab.columns:
        nm = col
        if col in col_info: nm=col_info[nm]

        if nm==tcol: continue # drop the time column

        hdr = {
            'id'                :col,
            'participant'       :participant,
            'sampling_frequency':SR,
            'modality'          :nm,
            'units'             :'V'}
        data = 3.3 * (np.array(tab[col]) / 1023) # express values as Voltage
        bio.add_channel((hdr,data))

    return bio



