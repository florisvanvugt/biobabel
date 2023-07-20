import biobabel as bb

import time
import neurokit2 as nk


bio = bb.Biodata()
bio.name = "Simulated data"
bio.meta['date']=time.strftime("%m/%d/%Y %H:%M:%S %Z%z")

SR = 1000
ecgA = nk.ecg_simulate(duration=15, sampling_rate=SR, heart_rate=80)
hdr = {
    'id'                :'a-ecg',
    'participant'       :'a',
    'sampling_frequency':SR,
    'modality'          :'ecg',
    'units'             :'mV'
}
bio.add_channel((hdr,ecgA))

ecgB = nk.ecg_simulate(duration=15, sampling_rate=SR, heart_rate=75)
hdr = {
    'id'                :'b-ecg',
    'participant'       :'b',
    'sampling_frequency':SR,
    'modality'          :'ecg',
    'units'             :'mV'
}
bio.add_channel((hdr,ecgB))

ppg = nk.ppg_simulate(duration=15, sampling_rate=1000, heart_rate=80)
hdr = {
    'id'                :'a-ppg',
    'participant'       :'a',
    'sampling_frequency':SR,
    'modality'          :'ppg',
    'units'             :'mV'
}
bio.add_channel((hdr,ppg))

bio.save('example.hdf5')


dat = bb.load('example.hdf5')
dat.print()
dat.plot()
