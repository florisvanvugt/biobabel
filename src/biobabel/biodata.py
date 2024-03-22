
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
        """ 
        Add metadata.

        k : the metadata key 
        v : the metadata value

        Example:
        biodata.add_meta('date','2024-03-22')
        """
        self.meta[k]=v

    def uniquefy(self,ident):
        """
        Return a channel id that is unique (does not exist yet), 
        as close as possible to the given id.

        ident : the id to start from

        If ident is already unique, it will be returned.
        """
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
        """ 
        Add the channel with specified header information and data.

        hdrdat : is a tuple (hdr,dat) where hdr is a dict containing the
        header and dat is the data stream itself (a one-dimensional array).
        """
        hdr,dat   = hdrdat
        newid     = hdr['id'].replace('/','_') # slashes don't work because HDF5 gets confused
        hdr['id'] = self.uniquefy(newid) # make the ID unique in case it already exists
        self.channels.append((hdr,dat))


    def find(self,crit={}):
        """ Find all channels that satisfy the metadata criteria and return them as (hdr,dat) """
        return [ self.get(ch) for ch in self.find_channels(crit) ]
            
            
        
        
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
        """ Return a list of participants in the current object """
        part = []
        for hdr,_ in self.channels:
            p= hdr.get('participant',None)
            if p and p not in part:
                part.append(p)
        part.sort()
        return part

    def get(self,chid):
        """ Get a particular channel data """
        for hdr,dat in self.channels:
            if hdr.get('id',None)==chid:
                return hdr,dat
        print("Could not find channel {}".format(chid))
        return None,None

    def get_time(self,chid):
        # Given a channel, reproduce a time vector
        hdr,dat = self.get(chid)
        t = np.arange(dat.shape[0])/hdr['sampling_frequency']
        return t

    def get_closest_sample(self,chid,t):
        """ Find the sample closest in time to the point t """
        hdr,dat = self.get(chid)
        idx = round( t * hdr['sampling_frequency'] )
        if idx<0: return 0
        return min(dat.shape[0],idx)


    
    def get_duration(self,chid=None):
        """ Get the duration of a channel in seconds """
        if chid==None: # If no channel is given, return maximum duration of all channels
            chids = self.find_channels()
            d = [ self.get_duration(c) for c in chids ]
            return np.max(d)
        
        hdr,dat  = self.get(chid)
        SR       = hdr['sampling_frequency']
        nsamp    = dat.shape[0]
        dur      = nsamp/SR
        return dur


    
    def summary(self):
        """ Return a summary of the current data (in str format) """
        ret = "Summary of {}\n".format(self.name)
        ret += self.summarize_meta()+"\n"
        if self.date and 'date' not in self.meta:
            ret += '[ date : {} ]\n'.format(self.date)

        for p in self.get_participants():
            ret += "Participant '{}'\n".format(p)
            chans = self.find_channels({"participant":p})
            for chan in chans:
                ret += "∟ {}\n".format(self.summarize_channel(chan))
            ret += "\n"

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

    

    def plot(self,channels=None,figsize=(12,7)):
        """ 
        Produce a simple inspection plot of the entirety of the data. 
        The channels argument can indicate a channel or a list of channels to be plotted.
        """

        import matplotlib.pyplot as plt

        chans = self.find_channels()
        if channels:
            if isinstance(channels,str):
                chans = [channels]
            else:
                chans = channels # assume it is a list
                
        if not len(chans):
            print("No channels to plot.")
            return

        def get_colors(N):
            import colorsys
            HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
            RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
            return list(RGB_tuples)

        COLORS = get_colors(len(chans))

        f,axs =plt.subplots(len(chans),1,sharex=True,figsize=figsize,squeeze=False)

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
                    ax.axvline(x=t,dashes=[2,2],color='gray')

        if self.name:
            plt.suptitle(self.name)
        plt.tight_layout()
        plt.show()





    # Make changes
    
    def rename(self,old_id,new_id):
        for hdr,_ in self.channels:
            if hdr['id']==old_id:
                hdr['id']=new_id
                return
        print("No channel found with ID {}".format(old_id))
        return 



    def update_channel(self,ident,specs):
        """ Update the header of a particular channel. """
        for hdr,_ in self.channels:
            if hdr['id']==ident:
                for k in specs:
                    #assert k!="id" # probably not safe to change channel ID that way
                    hdr[k]=specs[k]
                return # We're done, there should be only one channel with that ID
        print("No channel found with ID {}. Nothing updated.".format(ident))
        return
        

    def crop(self,tfrom=None,tend=None):
        """ Crop a number of seconds from the beginning or end of all channels. """
        if tfrom==None and tend==None: return # otherwise it doesn't really make sense eh?
        if tfrom==None: tfrom=-np.Inf
        if tend==None: tend=np.Inf
        newchannels = []
        for hdr,vals in self.channels:
            chan = hdr['id']
            t = self.get_time(chan)
            tincl = (t>tfrom) & (t<tend)
            vals = vals[tincl]
            newchannels.append((hdr,vals))
        self.channels = newchannels # replace

        # Need to also update the markers!
        for m in self.markers.keys():
            mrk = self.markers[m]
            self.markers[m] = [ t-tfrom for t in mrk
                                if t>tfrom and t<tend ]
            # This (also) drops markers that are no longer in the current range


    def drop(self,what):
        """ Drop channels. Provide an ID or a list of IDs for the channels to be dropped. """

        if isinstance(what,str):
            # Assume that this is the ID of the channel we want to drop so drop it
            self.channels = [ (hdr,vals) for (hdr,vals) in self.channels if hdr['id']!=what ]

        if isinstance(what,list):
            # Assume that this is a list of IDs of the channel we want to drop so drop them
            self.channels = [ (hdr,vals) for (hdr,vals) in self.channels if hdr['id'] not in what ]

        return self
    


    def select(self,what):
        """ Select only some channels and drop the others. 
        Provide an ID or a list of IDs for the channels to be retained. """

        if isinstance(what,str):
            # Assume that this is the ID of the channel we want to drop so drop it
            self.channels = [ (hdr,vals) for (hdr,vals) in self.channels if hdr['id']==what ]

        if isinstance(what,list):
            # Assume that this is a list of IDs of the channel we want to drop so drop them
            self.channels = [ (hdr,vals) for (hdr,vals) in self.channels if hdr['id'] in what ]

        if isinstance(what,dict):
            # Assume that this is a dictionary of metadata to characterize the channels you want to keep.
            # e.g. select({"participant":"a"}) means we only keep the data from participant "a".
            newchan = []
            for (hdr,vals) in self.channels:
                keep = True
                for k in what:
                    if hdr[k]!=what[k]:
                        keep = False
                if keep:
                    newchan.append((hdr,vals))
            self.channels = newchan

        return self
            

            

            

    def copy(self):
        """ Create a deep copy of oneself """
        
        bio = Biodata() # create a new biodata object

        bio.name = self.name
        bio.meta = self.meta.copy()

        for (ch,dat) in self.channels:
            bio.channels.append( (ch.copy(),dat.copy()) )
            
        bio.markers = {}
        for m in self.get_markers():
            bio.markers[m] = list(self.get_marker(m))

        return bio
        



            
            
    # Marker functionality 
    
    def get_markers(self):
        """ Returns a list of names of markers. """
        mrk= list(self.markers.keys())
        mrk.sort()
        return mrk

    def get_marker(self,m):
        """ For a given marker, returns a list of time points stored under that marker. """
        return self.markers.get(m,[])

    def add_marker(self,m,timepoints):
        """ Add a marker with a given label m and set of time points """
        if isinstance(timepoints,float):
            timepoints = [timepoints]
        self.markers[m] = timepoints

    def clear_markers(self):
        self.markers = {}
    



    #
    #
    #
    # Input/output
    #
    #
        
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
                dset.attrs['SR']          =hdr['sampling_frequency']
                dset.attrs['participant'] =p
                dset.attrs['modality']    =modality
                dset.attrs['units']       =hdr.get('units','arbitrary')

        hf.close()
