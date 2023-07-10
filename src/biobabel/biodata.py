
import numpy as np
import h5py
import time


class Biodata:
    """ 
    Represents a collection of streams of physiological data (channels)
    as well as some set of triggers (event markers).
    """

    
    def __init__(self):
        self.clear()


    def clear(self):
        """ Clear all data currently in the object """
        self.date         = ''
        self.channels     = []
        self.markers      = {}
        self.meta         = {} # miscellaneous metadata
        self.name         = ''


    def find_channels(self,crit={}):
        """ Find the channel id's satisfying certain criteria """
        chans = []
        for hdr,_ in self.channels:
            ok = True
            for k in crit:
                if hdr.get(k,None)!=crit[k]:
                    ok = False
            if ok:
                chans.append(hdr['id'])
        return chans


    def get_participants(self):
        part = []
        for hdr,_ in self.channels:
            p= hdr.get('participant',None)
            if p and p not in part:
                part.append(p)
        part.sort()
        return part

    def get(self,chid):
        # Get a particular channel data
        for hdr,dat in self.channels:
            if hdr.get('id',None)==chid:
                return hdr,dat


    def get_time(self,chid):
        # Given a channel, reproduce a time vector
        hdr,dat = self.get(chid)
        t = np.arange(dat.shape[0])/hdr['sampling_frequency']
        return t
    
            

    def summary(self):
        """ Return a summary of the current data (in str format) """
        ret = "Summary of {}\n".format(self.name)
        if self.date:
            ret += '[ date : {} ]\n'.format(self.date)
        for p in self.get_participants():
            ret += "\nParticipant '{}'\n".format(p)
            chans = self.find_channels({"participant":p})
            for chan in chans:
                ret += "∟ {}\n".format(self.summarize_channel(chan))

        if len(self.markers):
            ret += "\nMarkers:\n"
            for m in self.markers:
                ret += "∟ marker {} : {} events\n".format(
                    m,
                    len(self.markers[m]),
                )
        return (ret)



    def summarize_channel(self,chid):
        """ Return a string summary of the channel indicated by the given id. """
        hdr,dat  = self.get(chid)
        SR       = hdr['sampling_frequency']
        nsamp    = dat.shape[0]
        dur      = nsamp/SR

        ret = "channel {} [ modality {} in {} ] {} samples @ {:.1f} Hz = {:.1f} s".format(
            chid,
            hdr.get('modality','N/A'),
            hdr.get('units',   'N/A'),
            nsamp,
            SR,
            dur
        )

        return ret


    def print(self):
        summ = self.summary()
        print(summ)

    

    def plot(self):

        import matplotlib.pyplot as plt

        chans = self.find_channels()

        def get_colors(N):
            import colorsys
            HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
            RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
            return list(RGB_tuples)

        COLORS = get_colors(len(chans))

        f,axs =plt.subplots(len(chans),1,sharex=True,figsize=(12,7))

        for i,chan in enumerate(chans):
            ax = axs[i]
            hdr,vals = self.get(chan)
            t = self.get_time(chan)
            col = COLORS[i]
            ax.plot(t,vals,color=col)
            ax.set_title(chan)

        for m in self.get_markers():
            evs = self.get_marker(m)
            for t in evs:
                ax.axvline(x=t)

        if self.name:
            plt.suptitle(self.name)
        plt.tight_layout()
        plt.show()



        
        
    
    def get_markers(self):
        mrk= list(self.markers.keys())
        mrk.sort()
        return mrk

    def get_marker(self,m):
        return self.markers.get(m,[])


    

    def from_hdphysio5(self,fname):

        self.clear()
        
        # This file is included in bioread
        self.hf = h5py.File(fname,'r')
        self.name = fname

        bio = {}

        if 'participants' not in self.hf.attrs:
            print("# Error, missing participants attribute in the root.")
        if 'date' in self.hf.attrs:
            self.date = self.hf.attrs['date']
        self.participants = self.hf.attrs['participants']
        self.channels = []
        self.channels_by_type = {}
        for p in self.participants:
            for ch in self.hf[p].keys():
                nm = "{}/{}".format(p,ch)
                dset = self.hf[p][ch]
                if self.SR:
                    if dset.attrs['SR']!=self.SR:
                        print("## ERROR, sampling rate {} differs from that of other channels. Not currently implemented.")
                else:
                    self.SR=dset.attrs['SR']
                assert self.SR==dset.attrs['SR']
                bio[nm]=dset ##np.array(dset[:]) # convert into numpy array just to be sure
                mod = dset.attrs['modality']
                self.channels.append(nm)
                self.channels_by_type[mod] = self.channels_by_type.get(mod,[])+[nm]

        self.markers = {}
        for m in self.hf.attrs.get('markers',[]):
            self.markers[m] = self.hf.attrs[m] # get the markers in question
            
        bio['t']=np.arange(dset.shape[0])/self.SR # recreate a time vector

        self.bio = bio
        self.preprocessed = {}



        
        
    def save(self,fname):
        """
        Save current data file in hdphysio5 format

        fname : filename of the file to be created
        """

        if not fname.lower().endswith('.hdf5'):
            print("Currently only saving in hdphysio5 format.")
            return

        # Go ahead and save
        
        ## Create the HDF5 version
        hf = h5py.File(fname, "w")
        participants = self.get_participants() # set participants attribute
        if self.name:
            hf.attrs['name']=self.name
        hf.attrs['participants']=participants
        if self.date:
            hf.attrs['date']=self.date
        else:
            hf.attrs['date']=time.strftime("%m/%d/%Y %H:%M:%S %Z%z")


        # Create the markers --- TODO
        eventtypes = self.get_markers()
        if eventtypes:
            hf.attrs['markers']=eventtypes
            for e in eventtypes:
                evs = self.get_marker(e)
                hf.attrs[e]=evs


        for p in participants:
            dat = hf.create_group(p)

            # Find channels for this participant
            chans = self.find_channels({'participant':p})
            for chan in chans:
                hdr,dat = self.get(chan)
                modality = hdr['modality']
                sz = dat.shape[0]
                dset = hf[p].create_dataset(modality,(sz,),dtype='f',data=dat)
                dset.attrs['SR']=hdr['sampling_frequency']
                dset.attrs['participant']=p
                dset.attrs['modality']=modality
                dset.attrs['units']=hdr.get('units','arbitrary')

        hf.close()
