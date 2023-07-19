
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


    def summarize_meta(self):
        # Pretty printing courtesy of
        # https://stackoverflow.com/questions/54573444/how-to-print-key-value-pairs-of-a-dict-as-an-aligned-table
        if len(self.meta.keys()):
            max_key_len = max(map(len,self.meta)) # find the maximum key length
            format_string = '· {{key:{}}}  {{value}}\n'.format(max_key_len)
            toret = ""
            for key, value in self.meta.items():
                toret += (format_string.format(key=key, value=value))
            return toret
        else:
            return ""
        #return '\n'.join([ "· {}={}".format(k,self.meta[k]) for k in self.meta ])
        
    def add_meta(self,k,v):
        self.meta[k]=v

    def uniquefy(self,ident):
        ids = self.find_channels()
        if ident not in ids:
            return ident
        cnt = 1
        newid = "{}.{}".format(ident,cnt)
        while newid in self.find_channels():
            cnt += 1
            newid = "{}.{}".format(ident,cnt)
        return newid

    def add_channel(self,hdrdat):
        """ Add the channel with specified header information and data """

        hdr,dat = hdrdat
        hdr['id']=self.uniquefy(hdr['id']) # make the ID unique in case it already exists
        self.channels.append((hdr,dat))
        
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
        ret += self.summarize_meta()+"\n"
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

        units = 'in {} '.format(hdr['units']) if 'units' in hdr else ''
        
        ret = "channel {} [ modality {} {}] {} samples @ {:.1f} Hz = {:.1f} s".format(
            chid,
            hdr.get('modality','N/A'),
            units,
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
        if not len(chans):
            print("No channels to plot.")
            return

        def get_colors(N):
            import colorsys
            HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
            RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
            return list(RGB_tuples)

        COLORS = get_colors(len(chans))

        f,axs =plt.subplots(len(chans),1,sharex=True,figsize=(12,7),squeeze=False)

        for i,chan in enumerate(chans):
            ax = axs[i][0]
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

        # Create an empty dataset to hold meta attributes
        m = hf.create_dataset("meta", data=h5py.Empty("f"))
        for k in self.meta:
            m.attrs[k]=self.meta[k]

        # Create the markers
        eventtypes = self.get_markers()
        if eventtypes:
            hf.attrs['markers']=eventtypes
            for e in eventtypes:
                evs = self.get_marker(e)
                hf.attrs[e]=evs

        # Add the data channels for each participant
        for p in participants:
            dat = hf.create_group(p)

            # Find channels for this participant
            chans = self.find_channels({'participant':p})
            for chan in chans:
                hdr,dat = self.get(chan)
                modality = hdr['modality']
                sz = dat.shape[0]
                dset = hf[p].create_dataset(chan,(sz,),dtype='f',data=dat)
                dset.attrs['SR']=hdr['sampling_frequency']
                dset.attrs['participant']=p
                dset.attrs['modality']=modality
                dset.attrs['units']=hdr.get('units','arbitrary')

        hf.close()
