---
title: 'biobabel: a unified interface for reading a plethora of file formats for biosignals such as cardiac, respiration, electrodermal data'
tags:
  - biosignals
  - heart
  - breathing
  - PPG
  - ECG
  - file format
  - conversion
  - XDF
  - ACQ
  - HDF5
  - Python
authors:
  - name: Floris T. van Vugt
    orcid: 0000-0003-1739-0175 
    affiliation: 1
affiliations:
  - name: Department of Psychology, University of Montreal, Montreal, Canada
    index: 1
date: 28 October 2023
bibliography: paper.bib

---


# Statement of need

There is increasing interest on the part of the research community in biosignals: measurements of cardiac activity, electrodermal activity, respiration, and others. There are now wonderful packages for preprocessing ([@neurokit]) and analyzing ([@Brammer2020]) these signals. However, progress is hampered by the proliferation of a multitude of file formats. Each software package reads only a subset of these formats, requiring us to convert between them which is tedious and error-prone.

Major file formats at the time of writing:

+ EDF
+ XDF, a format used by open source labstreaminglayer (LSL).
+ OpenSignals
+ BDF
+ CSV
+ Acknowledge

What is needed is a package that is able to read each of these file format using a common interface. This means that code is portable and other software packages can capitalize on `biobabel` taking care of the nitty gritty of file format reading and focus instead on functionality.

Python packages exist that can read these data formats. However, each makes the data available in a different structure. This means that pipelines have to be changed when switching from one data format to another, which is tedious and error-prone. This situation is further complicated by the fact that different file formats make different assumptions about the data structure: in some cases signals in the same file are forced to have the same sampling rate (e.g. OpenSignals) whereas in other formats sampling rates can vary by signal (e.g. XDF). What is needed is a package that reads data into a standardized data format allowing data to be accessed in a transparent manner.

At the time of writing, `biobabel` is in active use at the [Human Connection Science Lab](https://connectionscience.org/) and the [International Laboratory for Brain, Music and Sound Research (BRAMS)](https://brams.org).





# Functionality

`biobabel` is a package that leverages existing Python packages that can already read a majority of biosignals data file formats. It furthermore capitalizes on existing packages such as [@matplotlib], [@numpy] and [@pandas].

Inspiration was taken from [`nibabel`](https://nipy.org/nibabel/) which is a Python library able to read virtually any neuroimaging file format in the known universe, and making it available in Python [@nibabel].


+ Seamless reading of a host of physiology data file format (XDF, OpenSignals).
+ Automatic guessing of file format that is reasonably robust (using cues such as file extension or ``sniffing'' if that is not sufficient to identify file format).
+ Cross-platform functionality since all code is pure-Python.
+ Generic CSV reading.
+ Quick-and-dirty command-line based previewing.
+ Streamlined module code that can easily be extended to read file formats not yet included.
+ Data is loaded into an object-oriented structure which allows for easy management of different signals, various sampling rates and multiple participants.


## Supported data formats

At the time of writing the following data formats are supported:

| Format                              | File extension(s) | Courtesy of                                                        | Support level |
|:-----------------------------------:|:-----------------:|:------------------------------------------------------------------:|:-------------:|
| Extensible Data Format              | .xdf              | [pyxdf](https://pypi.org/project/pyxdf/)                           | Rudimentary   |
| BIOSEMI 24-bit BDF                  | .bdf              | [pybdf](https://pypi.org/project/pybdf/)                           |               |
| BioPAC Acknowledge                  | .acq              | [bioread](https://pypi.org/project/bioread/)                       | Full          |
| OpenSignals (r)evolution / BiTalino | .txt              | [opensignalsreader](https://github.com/PGomes92/opensignalsreader) |               |
|                                     | .edf              |                                                                    |               |
	
Wishlist: https://github.com/holgern/pyedflib

## Easy previewing

`biobabel` provides simple accessible previewing of data files even from the command line.



## Multiple participants

Data for multiple participants is accomodated in the data structure by assigning each data channel a unique ID. An index is used to retrieve the channel ID for a given participant and a desired data stream.


## Usage

Simple usage example in Python:

```
import biobabel
bio = biobabel.load('filename.txt')
bio.print()
bio.plot()
bio.save('new_filename.hdf5')
```



# Acknowledgements
Mihaela Felezeu and Alex Nieva at BRAMS provided helpful tutorials on using all manners of biosignals.


# References
