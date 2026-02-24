__version__ = '1.0.7'


import biobabel.io
from biobabel.io import load

#from biobabel import * # lint doesn't like this - perhaps we can work without it.

from biobabel.biodata import Biodata

DATEFORMAT = "%Y/%m/%d %H:%M:%S %Z%z"

import sys

import argparse



def info():
    """
    Display quick information about a given file.
    """
  
    get_file('Display basic information about a physiology file.')


def get_file(descr=''):
    """
    Figure out which file wants to be opened.
    First check the command line if a file was indicated.
    If not, show a file selection dialog window to allow
    the user to select one.
    Open the file, and then print a summary.

    descr : A description of the purpose of the script for which this is done.
    """
    import os

    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument("filename", nargs="?", help="The file to open. If no file is provided, a window will open to ask you to select a filename.")
    parser.add_argument('-v','--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    if args.filename:
        fname = args.filename
    else:
        fname = ask_bio_file()
        

    if not fname:
        print("You need to select a file. Exiting now.")
        sys.exit(-1)

    if not os.path.exists(fname):
        print("File {} does not seem to exist. Exiting now.".format(fname))
        sys.exit(-1)
        
    bio = biobabel.io.load(fname)
    bio.print()
    bio.meta['filename']=fname
    return bio
    


def ask_bio_file():
    """
    Display a file selection dialogue to ask the user to select an input file.
    """
    from tkinter import filedialog as fd
    
    filetypes = biobabel.io.get_compatible_file_types()+[
        ('All files', '*.*')
        ]

    fname = fd.askopenfilename(
        title='Select your recording',
        initialdir='.',
        filetypes=filetypes)

    return fname
    




def display(advanced=False):
    """ 
    Produce a quick plot of a file.
    
    advanced : if True, show the advanced viewer (TK GUI) otherwise show a simple matplotlib 
    """

    bio = get_file("Produce a quick plot of the contents of a physiology file.")

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
    """
    Convert a file to the biobabel native HDF5 format.
    """
    bio = get_file('Convert a file to the biobabel-native HDF5 format.') # attempt to get a file name to work on
    fname = bio.meta['filename']
    import os
    fbase,ext = os.path.splitext(fname)
    targetf = '{}.hdf5'.format(fbase)
    bio.save(targetf)
    print("Saved to {}".format(targetf))



def split():
    """
    Split a file according to its markers.
    That is, given a file with several channels and markers, produce a set of files that each contain
    the portion of signal between subsequent markers.
    """
    bio = get_file('Split file into smaller files along time markers.') # attempt to get a file name to work on
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

    parser = argparse.ArgumentParser(description='Merge a series of physiology files by concatenating them in time.')
    parser.add_argument("infile", nargs="+", help="The files to include in the merge.")
    parser.add_argument("outfile", help="The output file name.")
    parser.add_argument('-v','--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    if not args.outfile:
        print("You need to supply an output file name.")
        sys.exit(-1)
    else:
        outf = args.outfile

    if not args.infile:
        print("You need to supply at least one input file.")
        sys.exit(-1)
    else:
        infs = args.infile

    print("Input files: {}".format(",".join(infs)))
    print("Output file: {}".format(outf))

    inputs = []
    for inf in infs:
        bio = biobabel.io.load(inf)
        if bio:
            inputs.append(bio)
        else:
            sys.exit(-1)


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
    Create an user friendly report giving an overview of a whole series of physiology files at once.
    """

    parser = argparse.ArgumentParser(description='Produce a quick overview of a range of physiology files.')
    parser.add_argument("filename", nargs="+", help="The files to include in the report.")
    parser.add_argument('-v','--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    if not args.filename:
        sys.exit(-1)

    infs = args.filename
    print("Input files: {}".format(",".join(infs)))

    html = ""
    for inf in infs:
        print()
        print("==> {}".format(inf))
        bio = biobabel.io.load(inf)
        if bio:
            h = bio.html_report()
            html += "<h1><a id=\"{}\">{}</a></h1><p>{}</p>".format(inf,inf,h)
        else:
            sys.exit(-1)


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

    outf = 'report.html'
    with open(outf,'w') as f:
        f.write(final)

    print("Report written to {}".format(outf))


        




def guess_modality(s):
    """ 
    Guess modality from a channel label.
    """
    if s.lower().find('ecg')>-1:
        return 'ecg'
    if s.lower().find('ppg')>-1:
        return 'ppg'
    if s.lower().find('resp')>-1:
        return 'resp'
    if s.lower().find('eda')>-1:
        return 'eda'
    return 'unknown'

