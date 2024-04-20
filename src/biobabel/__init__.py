from biobabel.io import load

from biobabel import *

from biobabel.biodata import Biodata

DATEFORMAT = "%Y/%m/%d %H:%M:%S %Z%z"

import sys


def info():
    """
    Display quick information about a given file.
    """
    get_file()


def get_file():
    """
    Figure out which file wants to be opened.
    First check the command line if a file was indicated.
    If not, show a file selection dialog window to allow
    the user to select one.
    Open the file, and then print a summary.
    """
    import os
    from tkinter import filedialog as fd

    fname = None
    if len(sys.argv)>1:
        fname = sys.argv[1]
    else:

        filetypes = (
            ('All files', '*.*'),
            ('HDF5 dataset', '*.hdf5')
        )

        fname = fd.askopenfilename(
            title='Select your recording',
            initialdir='.',
            filetypes=filetypes)

    if not fname:
        print("You need to select a file. Exiting now.")
        sys.exit(-1)

    if not os.path.exists(fname):
        print("File {} does not seem to exist. Exiting now.".format(fname))
        sys.exit(-1)
        
    bio = load(fname)
    bio.print()
    bio.meta['filename']=fname
    return bio
    



def display(advanced=False):
    """ 
    Produce a quick plot of a file.
    
    advanced : if True, show the advanced viewer (TK GUI) otherwise show a simple matplotlib 
    """

    bio = get_file()

    if advanced:
        import biobabel.viewer as viewer
        viewer.main(bio)

    else:
        #Simpler version:
        bio.plot()



def view():
    """ 
    Display advanced viewer of a given data file. 
    """
    display(advanced=True)




def guess_modality(nm):
    """ 
    Guess the modality (e.g. ECG) from the 
    label of a signal column.
    """
    l = nm.lower()
    for mod in ['ecg','eda','gsr','ppg']:
        if l.find(mod)>-1:
            return mod
    return nm
    



def tohdf5():
    """ Split a file according to its markers """
    bio = get_file() # attempt to get a file name to work on
    fname = bio.meta['filename']
    import os
    fbase,ext = os.path.splitext(fname)
    targetf = '{}.hdf5'.format(fbase)
    bio.save(targetf)
    print("Saved to {}".format(targetf))



def split():
    """ Split a file according to its markers """
    bio = get_file() # attempt to get a file name to work on
    # If we're still here that means we have loaded a file

    # Extract all the markers, throw them on a big heap
    ts = []
    for m in bio.get_markers():
        ts += bio.get_marker(m)

    if 0 not in ts: ts.append(0)
    d = bio.get_duration()
    if d not in ts: ts.append(d)
    ts.sort()
    
    if len(ts)<3:
        print("Only {} time points (including beginning and ending). Not enough to split.")
        sys.exit(0)

    fname = bio.meta['filename']
    import os
    fbase,ext = os.path.splitext(fname)
        
    tprev = ts[0]
    for i,t in enumerate(ts):

        if abs(t-tprev)>0:
            targetf = "{}_{:03d}{}".format(fbase,i,'.hdf5')
            print("Cutting {} to {} => {}".format(tprev,t,targetf))
            # cut between tprev and t

            sub = bio.copy()
            sub.crop(tprev,t)
            sub.meta['filename']=targetf

            # Write file to hdf5 copy
            sub.save(targetf)
            
        tprev = t
    





def merge():
    """ 
    Merge multiple files into a single file.
    This assumes data from the channels in the input files are all synchronous.
    """

    if len(sys.argv)<3:
        print("Usage: biomerge <FILE1> <FILE2> ... <OUTPUT_FILE>")
        print("Need at least two input files")
        sys.exit(-1)

    outf = sys.argv[-1]
    infs = sys.argv[1:-1]

    print("Input files: {}".format(",".join(infs)))
    print("Output file: {}".format(outf))

    inputs = []
    for inf in infs:
        bio = load(inf)
        inputs.append(bio)


    merged = Biodata() # create a new object
    for bio in inputs:
        merged.merge(bio)

    merged.print()
    merged.save(outf)
    





HTML_CSS_STYLE = """

.sidenav {
  height: 100%;
  width: 200px;
  position: fixed;
  z-index: 1; 
  top: 0; 
  left: 0;
  background-color: #111;
  overflow-x: hidden; 
  padding-top: 20px;
}

.sidenav a {
  padding: 6px 8px 6px 16px;
  text-decoration: none;
  font-size: 18px;
  color: #818181;
  display: block;
}

.sidenav a:hover {
  color: #f1f1f1;
}

.main {
  margin-left: 200px; /* Same as the width of the sidebar */
  padding: 0px 10px;
}

@media screen and (max-height: 450px) {
  .sidenav {padding-top: 15px;}
  .sidenav a {font-size: 18px;}
}

"""


def html_report():
    """
    Create an easy report of a whole series of files at once.
    """

    if len(sys.argv)<2:
        print("Usage: biohtml <FILES>")
        sys.exit(-1)
    
    infs = sys.argv[1:]
    print("Input files: {}".format(",".join(infs)))

    html = ""
    for inf in infs:
        print()
        print("==> {}".format(inf))
        bio = load(inf)
        h = bio.html_report()
        html += "<h1><a id=\"{}\">{}</a></h1><p>{}</p>".format(inf,inf,h)


    ## Add header

    links = [ "<a href=\"#{}\">{}</a>".format(inf,inf) for inf in infs ]
    
    final = """
<html>

<head>
<style>
{}
</style>
</head>

<body>
<!-- Side navigation -->
<div class="sidenav">
{}
</div>

<!-- Page content -->
<div class="main">
  {}
</div>
</body>
</html>""".format(
    HTML_CSS_STYLE,
    "\n".join(links),
    html)
        
    with open('report.html','w') as f:
        f.write(final)


        
