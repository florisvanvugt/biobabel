


import tkinter
from tkinter import filedialog as fd
from tkinter import font as tkFont  # for convenience
from tkinter import Toplevel
import tkinter.messagebox
from tkinter.messagebox import askyesno

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton

import numpy as np
import pandas as pd
import os
import scipy.signal

import json

import sys


# Globals we carry around
gb = {}





def check_window_zoom(t):

    if gb['WINDOW_T']>PEAK_EDIT_MAX_WINDOW_T:

        # First zoom in
        update_window(.8*PEAK_EDIT_MAX_WINDOW_T/gb['WINDOW_T'],t)
        
        return False

    return True



def update_cursor():
    x = gb['cursor.t']
    for c in gb['cursor']:
        c.set_data([x, x], [0, 1])
    #gb['cursor.intvl'].set_data([x, x], [0, 1])

    #x = gb['cursor.snap.t']
    #if gb['cursor.snap']:
    #    if x:
    #        gb['cursor.snap'].set_data([x], [get_signal_at_t(x)])

    gb['canvas'].draw()


    


def on_move(event):
        
    if event.xdata:
        t = event.xdata
        gb['cursor.t']=t
        #if event.modifiers and 'shift' in event.modifiers:
        #    gb['cursor.snap.t']=snap_to_closest_peak(event.xdata)
        #else:
        gb['cursor.snap.t']=None
        update_cursor()
    




# When toggling the zoom, toggle between micro and macro window size
TOGGLE_WINDOW_SIZES = [ 1.5, 30 ]
            

def toggle_zoom():
    # Switch between zoom modes: micro and macro, to allow quick zooming
    wint = gb['WINDOW_T']
    sizedist = [ np.abs(np.log(wint/t)) for t in TOGGLE_WINDOW_SIZES ]
    target = TOGGLE_WINDOW_SIZES[np.argmax(sizedist)]
    if False:
        print("Toggling!")
        print(wint)
        print(sizedist)
        print(target)
    update_window(target/wint,gb['cursor.t'])
    


    
def process_key_events(event):
    #if event.key=='left': back_in_time()
    #if event.key=='right': forward_in_time()

    if event.char=='z':
        toggle_zoom()
    if event.char=='a':
        tmax = gb['tmax']
        #tmax = max(gb['t'])
        gb['tstart']=0
        gb['WINDOW_T']=tmax
        update_window_definitions()
        redraw_all()


        

def process_scroll_events(event):

    if 'ctrl' in event.modifiers:

        # Zoom
        t = event.xdata
        
        if event.step>0:
            window_wider(t)
        if event.step<0:
            window_narrower(t)

    else:

        # Pan
        
        if event.step<0:
            back_in_time()
        if event.step>0:
            forward_in_time()
        
        


def on_closing():
    gb['root'].destroy()
    sys.exit(0)
    

def quit():
    on_closing()


def redraw_all():
    redraw()


def back_in_time(e=None):
    gb['tstart']-=gb['WINDOW_SHIFT_T']*gb['WINDOW_T']
    redraw_all()

def forward_in_time(e=None):
    gb['tstart']+=gb['WINDOW_SHIFT_T']*gb['WINDOW_T']
    redraw_all()
    

def jump_back_in_time(e=None):
    gb['tstart']-=.95*gb['WINDOW_T']
    redraw_all()

def jump_forward_in_time(e=None):
    gb['tstart']+=.95*gb['WINDOW_T']
    redraw_all()
    


def set_window(e=None):
    # When the slider is used to move to a new portion of the signal
    new_val = gb['slider'].get()
    gb['tstart']=int(new_val)*gb['WINDOW_T']
    redraw_all()


# When we zoom in or out, by what proportion shall we change the window width?
WINDOW_CHANGE_FACTOR = 1.25


def restore_t(t_target,prop):
    # Return what window edge (left window edge) you need to
    # get the time t at the given proportion of the width.
    # I know, sounds complicated...
    #print("Prop {} Window {} T-target {}".format(prop,gb['WINDOW_T'],t_target))
    tstart = t_target- prop*gb['WINDOW_T']
    #print(tstart)
    return tstart
    

def update_window(fact,around_t):
    # Determine what we want to center around
    if not around_t: around_t = gb['tstart']+gb['WINDOW_T']/2
    t_prop = (around_t-gb['tstart'])/gb['WINDOW_T'] # get at what proportion of the window that time point is located
    gb['WINDOW_T']*=fact
    gb['tstart']= restore_t(around_t,t_prop)
    update_window_definitions()
    ##print(gb['tstart'])
    redraw_all()

def window_wider(around_t=None):
    update_window(1/WINDOW_CHANGE_FACTOR,around_t)

def window_narrower(around_t=None):
    update_window(WINDOW_CHANGE_FACTOR,around_t)
    
def get_n_windows():
    return int(np.floor(gb['tmax']/gb['WINDOW_T']))

def update_window_definitions():
    # If the window width has changed, cascade the necessary updates
    nwind = get_n_windows()
    gb['slider'].configure(to=nwind)
    



    
def make_plot():
    # Get the currently selected subplots
    # and show just these.
    # Effectively, it recreates figures and subplots
    try: 
        gb['canvas'].get_tk_widget().destroy()
    except:
        pass

    fig,axs = plt.subplots(gb['n.signals'],1,sharex=True,squeeze=False)
    gb['fig']=fig
    gb['axs']=axs #[0] # the main plot

    canvas = FigureCanvasTkAgg(fig, master=gb['root'])  # A tk.DrawingArea.
    canvas.get_tk_widget().pack()
    gb['canvas']=canvas

    #canvas.mpl_connect("key_press_event", process_key_events)
    canvas.mpl_connect("key_press_event", key_press_handler)
    # Bind the button_press_event with the on_click() method
    #canvas.mpl_connect('button_press_event', on_click)
    canvas.mpl_connect('motion_notify_event', on_move)

    canvas.mpl_connect("scroll_event", process_scroll_events)
    
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
    redraw()



ALPHA = .8



TARGET_PLOT_POINTS = 2000
# how many points to actually plot in the current window (approximately)
# If the truly available data is more than this, we downsample just for display purposes

def redraw():
    
    # Determine drawrange
    drawrange = (gb['tstart'],gb['tstart']+gb['WINDOW_T'])
    tmin,tmax = drawrange

    gb['cursor']= [None for _ in range(gb['n.signals']) ]
    
    for i,chan in enumerate(gb['channels']):
        ax = gb['axs'][i][0]
        ax.cla() # clear the axes

        #c = gb['channel']

        # Plot on axis
        #biodata = gb['biodata']
        #SR = gb['SR']

        #check if there's a rounding error causing differing lengths of plotx and signal
        #ecg_target = gb['ecg-prep-column']
        #ecg = gb['signal'] #biodata.bio[ecg_target] # gb['ecg_clean']
        ##print(ecg.shape)
        toplot = gb['data'][chan]

        t = toplot['t']
        #prep = biodata.preprocessed[ecg_target]
        tsels = (t>=tmin) & (t<=tmax)

        gb['cursor'][i] = ax.axvline(x=gb['cursor.t'],lw=1,color='blue',alpha=.9,zorder=99999)

        # Plot the actual signal
        x = t[tsels]
        y = toplot['vals'][tsels]

        nplot = sum(tsels) ## the number of samples we'd plot if we don't do sub-sampling

        factor = int(nplot/TARGET_PLOT_POINTS)
        if factor>1:
            x,y = x[::factor],y[::factor]

        pch = '-'
        if nplot<100:
            pch = 'o-'

        ax.plot(x,y,
                pch,
                label='cleaned',
                zorder=-10,
                color=gb['COLORS'][i])

        ax.set_ylabel(chan)
        ax.set_xlabel('t(s)')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)


        # Now determine the ylim scale
        AUTOSCALE = False # whether to use the matplotlib default scale
        if not AUTOSCALE:

            ## Remove the "invalid" portions of the signal too
            mn,mx = np.min(y),np.max(y)

            # add some padding on the sides
            pad = .025*(mx-mn)
            ax.set_ylim(mn-pad,mx+pad)
    
    #ax.set_xlim(gb['tstart'],gb['tstart']+WINDOW_T)
    update_axes()


def update_axes():
    axs = gb['axs']
    tend = gb['tstart']+gb['WINDOW_T']
    gb['slider'].set(int(gb['tstart']/gb['WINDOW_T']))

    axs[0][0].set_xlim(gb['tstart'],tend) # just by setting one the others should be linked hence follow
        
    plt.tight_layout()
    gb['canvas'].draw()
    

def get_colors(N):
    import colorsys
    HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    return list(RGB_tuples)

    

def main(bio):


    # Main window dimensions
    window_w,window_h=1300,450


    # Globals to carry around

    gb["WINDOW_T"] =15 # default window width in seconds
    gb['WINDOW_SHIFT_T'] =.2 # proportion of the window to shift when we go back and forth in time


    gb['qc']={}
    gb['invalid']= []
    gb['peaks']= []
    gb['cursor.t']=0



    ##
    ##
    ## Select file to open
    ##
    ##

    chans = bio.find_channels()
    gb['channels'] = chans
    if not len(chans):
        print("No channels to plot.")
        return

    gb['n.signals']= len(chans)
    gb['COLORS'] = get_colors(len(chans))

    gb['data'] = {}
    gb['tmin']=np.Inf
    gb['tmax']=-np.Inf
    for c in chans:
        hdr,vals = bio.get(c)
        t = bio.get_time(c)
        gb['tmin']=min([gb['tmin'],min(t)])
        gb['tmax']=max([gb['tmax'],max(t)])
        gb['data'][c]={"hdr":hdr,
                       "vals":vals,
                       "t":t}

        
    
    #if pc:
    #    pass
        #gb['channel'] = pc
        #gb['t']=bio.get_time(pc)
        #hdr,dat = bio.get(pc)
        #gb['SR']=hdr['sampling_frequency']
        #gb['hdr']=hdr

        # Also make a filtered version
        #METHOD = 'engzeemod2012'
        #METHOD = 'neurokit2'
        #METHOD
        #print("Filtering ECG signal using {} procedure in neurokit2".format(METHOD))
        #signal_flt = dat #neurokit2.ecg_clean(dat,sampling_rate=gb['SR'],method=METHOD)

        #sos = butter(15, 3, 'low', fs=gb['SR'], output='sos')
        #filtd = signal.sosfiltfilt(sos, dat)
        #gb['filtered']=filtd
        #gb['raw']=dat
        #gb['signal']=signal_flt

    #else:
        #sys.exit(-1)



    # See if there is an existing peak file

    # Create the interface
        
    root = tkinter.Tk()
    root.wm_title("Physio Peak Picker - {}".format(bio.name))
    root.geometry('{}x{}'.format(window_w,window_h))
    gb['root']=root





    gb['tstart']=0 # the left edge of the window we're currently showing

    # Current markers
    gb['mark_in']  =None
    gb['mark_out'] =None

        


    if 'peaks' not in gb:
        gb['peaks']=[]



    # Build the interface
    
    navf = tkinter.Frame(root)
    tkinter.Grid.columnconfigure(navf, 0, weight=1)
    navf.pack(side=tkinter.BOTTOM)
    bigfont = tkFont.Font(family='Helvetica', size=28, weight='bold')
    button_wid  = tkinter.Button(master=navf, text="+", command=window_wider,    font=bigfont)
    button_narr = tkinter.Button(master=navf, text="-", command=window_narrower, font=bigfont)
    button_wid.grid(column=0,row=0,padx=0, pady=10)
    button_narr.grid(column=1,row=0,padx=0, pady=10)


    button_back = tkinter.Button(master=navf, text="<", command=back_in_time, font=bigfont)
    button_forw = tkinter.Button(master=navf, text=">", command=forward_in_time, font=bigfont)
    button_back.grid(column=2,row=0,padx=10, pady=10)
    button_forw.grid(column=4,row=0,padx=10, pady=10)

    slider_update = tkinter.Scale(
        navf,
        from_=0,
        to=get_n_windows(),
        length=300,
        orient=tkinter.HORIZONTAL,
        label="")
    slider_update.bind("<ButtonRelease-1>",set_window)
    slider_update.grid(column=3,row=0,padx=10,pady=10)
    gb['slider']=slider_update





    # Packing order is important. Widgets are processed sequentially and if there
    # is no space left, because the window is too small, they are not displayed.
    # The canvas is rather flexible in its size, so we pack it last which makes
    # sure the UI controls are displayed as long as possible.
    #toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
    #canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    root.protocol("WM_DELETE_WINDOW", on_closing)


    root.bind("<Left>",back_in_time)
    root.bind("<Right>",forward_in_time)
    root.bind("<Prior>",jump_back_in_time) # page_up
    root.bind("<Next>",jump_forward_in_time) # page_down
    root.bind("<Key>",process_key_events)

    make_plot()
    redraw()



    tkinter.mainloop()



