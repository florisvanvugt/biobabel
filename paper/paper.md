---
title: 'biobabel: a unified interface for reading a plethora of file formats for biosignals such as cardiac, respiration, electrodermal data'
tags:
  - biosignals
  - physiology
  - heart
  - breathing
  - respiration
  - PPG
  - ECG
  - EDA
  - file format
  - conversion
  - XDF
  - EDF
  - labstreaminglayer
  - ACQ
  - HDF5
  - Python
authors:
  - given-names: Floris Tijmen
    non-dropping-particle: van
	surname: Vugt
    orcid: 0000-0003-1739-0175 
    affiliation: "1, 2, 3, 4, 5"
affiliations:
  - name: Department of Psychology, University of Montreal, Montreal, Canada
    index: 1
  - name: International Laboratory for Brain, Music and Sound Research (BRAMS), Montreal, Canada
    index: 2
  - name: Centre for Research on Brain, Language and Music (CRBLM), Montreal, QC, Canada
    index: 3
  - name: Centre Interdisciplinaire de Recherche sur le Cerveau et l'Apprentissage (CIRCA), Montreal, QC, Canada
    index: 4
  - name: Haskins Laboratories, Yale University, New-Haven CT, USA	
    index: 5
date: 20 March 2024
bibliography: paper.bib

---



# Summary

Human biosignals such as breathing, cardiac rhythms or skin conductance contain a wealth of insights into cognition, emotion and social connection. Measuring these biosignals is now possible through a range of sensors. However, each of these sensors and the accompanying software typically stores data in proprietary, specific file formats. This makes it difficult for researchers across the globe to build and share analysis software that can be used by all. Biobabel is a software package that reads all the major biosignal file formats and allows programmers to access the data in a straight-forward manner. It provides a handy set of tools for inspecting and performing basic data manipulations. Biobabel thus hopes to contribute to a practical foundation allowing researchers interested in biosignal to share analysis software across the globe.



# Statement of need

There is increasing interest on the part of the neuroscience and psychology research community in biosignals, that is, measurements of cardiac activity, electrodermal activity, respiration, and others [@Massaro2016;@Varga2017;@Horvers2021;@PosadaQuintero2020]. There are now wonderful packages for preprocessing [@neurokit] and analyzing [@Brammer2020] these signals. However, progress is hampered by the proliferation of a multitude of file formats (EDF, XDF, OpenSignals, BDF, CSV, Acknowledge ACQ). Existing software packages read only a subset of these formats, requiring us to convert between them which is tedious and error-prone. Furthermore, data in these different formats is typically organized differently, requiring researchers to reorganize their code to cater to different formats. This hampers the development of unified, reproducible pipelines that can be shared between research groups across the globe.

What is needed is a software platform that is able to read each of these file format using a common interface. Essentially, what is needed is a software layer that abstracts away from the nitty-gritty specifics of each format and can read all the major physiology file formats and make the data available through a unified API (application programming interface). Many of the physiological processing tools (e.g. biopeaks [@Brammer2020], or `neurokit2`), typically are only able to read from one or two of the data formats. This means that files in other formats first have to be converted from one format into the other before they can be used. This conversion is usually not straight forward since some formats have specific assumptions that others do not, and libraries that read these formats in Python for example do so into different structures. What is needed is a unified interface for accessing biosignal files.

To my knowledge, no such software package exists to date. Individual Python packages exist that can each read one these data formats. However, each makes the data available in a different structure. This means that pipelines have to be changed when switching from one data format to another, which is tedious and error-prone. This situation is further complicated by the fact that different file formats make different assumptions about the data structure: in some cases signals in the same file are forced to have the same sampling rate (e.g. OpenSignals) whereas in other formats sampling rates can vary by signal (e.g. XDF). In some cases the signals are supposed to have the same onset time (e.g. EDF) whereas other formats allow different onset times requiring re-aligning (e.g. XDF). What is needed is a software package that can read these diverse format into a reasonably flexible data structure that abstracts away from these differences: a package that reads data from a variety of data formats and making it available in a standardized, transparent manner.

Furthermore, existing software packages typically are unable to write files, meaning that intermediate processing steps have to be saved into a different, custom file format. What is needed is a software package that can straightforwardly write data in a sensible data format.

It is also important for physiological software to accommodate data from multiple participants. There is increasing interest in neuroscience in collecting physiological data simultaneously from multiple participants interacting in real-time [@Kelsen2022]. Such *hyperscanning* studies place unique demands on file structures that classically were designed for data from single participants only.

These problems were already solved for neuroimaging data using the *nibabel* package [@nibabel]. But for the physiology data, surprisingly such a software suite is missing, until now. 


# Functionality

`biobabel` is a package that leverages existing Python packages that can already read a majority of biosignals data file formats. It furthermore capitalizes on existing packages such as [@matplotlib], [@numpy] and [@pandas]. Its main functionalities are:

+ Seamless reading of a host of physiology data file formats.

+ Data is loaded into a structure supporting multiple data streams, markers, various sampling rates and multiple participants within a single object.

+ Convenient data manipulation (cropping in time, selecting subsets of channels, etc.) and previewing not typically implemented in existing software packages.

+ A set of quick-and-dirty command-line based previewing and basic data manipulation.

+ Streamlined modular code that allows the software package to be easily extended to read file formats not yet included.

+ Data can be written to an open standard file format based on [HDF5](https://www.hdfgroup.org/solutions/hdf5/).


## Supported data formats

At the time of writing the following data formats are supported:

| Format                              | File extension(s) | Supported by                                                        |
|:-----------------------------------:|:-----------------:|:------------------------------------------------------------------:|
| Extensible Data Format              | .xdf              | [pyxdf](https://pypi.org/project/pyxdf/)                           |
| BIOSEMI 24-bit BDF                  | .bdf              | [pybdf](https://pypi.org/project/pybdf/)                           |
| BioPAC Acknowledge                  | .acq              | [bioread](https://pypi.org/project/bioread/)                       |
| OpenSignals (r)evolution / BiTalino | .txt              | [opensignalsreader](https://github.com/PGomes92/opensignalsreader) |
| European Data Format                | .edf              | [pyedflib](https://pyedflib.readthedocs.io/en/latest/)             |
| Generic CSV                         | .csv              | Custom developed code including sniffing and educated guesses      |
| hdphysio5                           | .hdf5             | Native format developed specifically for biobabel                  |

The file format to be used is guessed automatically at the time of reading, using clues such as file extension, but if these are insufficiently informative, guesses are made based on sniffing of the file. For some file formats, such as CSV, the way these formats are used varies between research groups: essentially, CSV is a table format, but the meaning and names of various columns in this table are not specified. In those cases, `biobabel` will try to guess the meaning of the various columns, for example automatically guessing one column to be a time column if its values are increasing almost always by the same amount.

For instance, within Python the following code is sufficient to read a data file:
```python
import biobabel as bb
bio = bb.load('tests/example.hdf5')
```

Then, we can view properties of the data file:
```python
bio.print()
```

This will produce an overview of the dataset indicating sampling frequencies and durations:
```
Summary of Simulated data
· date  07/20/2023 10:48:32 EDT-0400

Participant 'a'
∟ channel a_ecg [ modality ecg ] 15000 samples @ 1000.0 Hz = 15.0 s
∟ channel a_ppg [ modality ppg ] 15000 samples @ 1000.0 Hz = 15.0 s

Participant 'b'
∟ channel b_ecg [ modality ecg ] 15000 samples @ 1000.0 Hz = 15.0 s
```

And easily inspect the data using a plot:

```python
bio.plot()
```

Which produces:

![Overview plot of sample data file, indicating each channel as a separate panel.\label{fig:simdataplot}](simdataplot.png)




## Biobabel internal data structure

Biobabel represents physiological datasets using a `Biodata` object (`bio` in the above example). Under the hood, this object contains a number of data streams, each of which is a single dimension array with some associated metadata, such as sampling frequency, participant ID, or yet others. Each data stream is identified with a unique ID.

The channel metadata allows us to easily find channels by data type or participant ID:

```python
bio.find_channels({"modality":"ecg"}) # find all channels containing ECG data
```

which returns a set of channel IDs: `['a_ecg', 'b_ecg']`.

The channel IDs can be used to query the channel metadata (in dictionary format) and extract its data:

```python
hdr,dat = bio.get('a_ecg')
hdr # find the associated metadata for this channel
```

which returns the metadata in `hdr`:

```
{'id': 'a_ecg',
 'participant': 'a',
 'sampling_frequency': 1000,
 'modality': 'ecg'}
```

In `biobabel`, each data stream can have its own sampling frequency, but all data streams are assumed to start at the same time. In my experience as physiological data analyst, this common starting time was a sensible assumption, since it holds true in most applications and making this assumption simplifies subsequent data handling. For data formats in which this assumption does not necessarily hold true (e.g. XDF), data loaded into `biobabel` will be cropped by the software package to a common starting point.

Biobabel also supports *markers*, which are points in time at which specific events are marked to occur. This can be start/stop markers indicating separate recording segments (as used in BioPAC Acknowledge file format). Markers are stored in the Biodata object and can be accessed using `bio.get_markers()` (to find the marker names) and `bio.get_marker(<NAME>)` (to extract the corresponding time points). In default plotting functions of `biobabel` they are indicated with dashed vertical lines (\autoref{fig:simdataplot}).

Biobabel allows a number of typical data management steps that most packages do not straight-forwardly allow, such as cropping the data to a selected time range (`bio.crop(t_start,t_end)`) and dropping or selecting channels.

Finally, data can be saved in the `biobabel` native HDF5-based format (`bio.save`)

For labs engaging in hyperscanning, `biobabel` seamlessly accomodates support for data from multiple participants. Each data stream can be allocated to a specific participant, allowing the software to find all participants `bio.get_participants()` or get channels for a specific participant (`bio.find_channels({'participant':'b'})`).



## Easy previewing and some manipulation from the command line

`biobabel` provides simple accessible previewing of data files even from the command line. This functionality is inspired by AFNI [@Cox_1996], which is a toolbox of shell scripts for neuroimaging analysis.

The following shell scripts are included:

+ `bioinfo <filename>` which reads the data file and prints a summary (a wrapper around `biodata.print()`)
+ `biobabel <filename>` which reads the data file and produces a simple plot (a wrapper around `biodata.view()`)
+ `tohdf5 <filename>` which converts a data file in any of the supported formats into biobabel's native HDF5 format.
+ `biosplit <filename>` which splits the data along its integrated markers (which often correspond to different recording sessions) into multiple separate files (e.g. `<filename_001>`, `<filename_002>` etc.)
+ `bioview <filename>` which launches a graphical user interface (GUI) reader allowing interactive inspection of data as shown below.

![Bioview is a GUI allowing the user to inspect a data file by zooming and navigating the entire signal.\label{fig:bioview}](bioview.png)



## Integration with biosignals processing packages

Since `biobabel` takes care of all the peculiarities of data files, processing pipelines can be substantially simplified. The following boilerplate code reads a data file in any of the supported file formats and automatically extracts the ECG columns and preprocesses the data using third-party library `neurokit2`:

```python
import neurokit2
import biobabel as bb
x = bb.load('dataset_copy.hdf5')
prep = {}
for hdr,signal in x.find({'modality':'ecg'}):
    prep[hdr['id']] = neurokit2.ecg_process(signal,sampling_rate=hdr['sampling_frequency'])
```




# Conclusion

It is hoped that `biobabel` will simplify the lives of scientists by abstracting away from the specifics of file formats. Using this package, data processing pipelines can be homogenized across research groups relying on different sensors, increasing much needed reproducibility. At the time of writing, `biobabel` is actively being used at the [Human Connection Science Lab](https://connectionscience.org/) and the [International Laboratory for Brain, Music and Sound Research (BRAMS)](https://brams.org). 



# Acknowledgements

Mihaela Felezeu and Alex Nieva at BRAMS provided helpful tutorials on using all manners of biosignals. Inspiration for `biobabel` was taken from [`nibabel`](https://nipy.org/nibabel/) which is a Python library able to read virtually any neuroimaging file format in the known universe, and making it available in a unified Python interface [@nibabel]. We thank the contributors of that package for their excellent work.



# References
