

# Biobabel : a unified interface for reading a plethora of physiology file formats

Many different file formats exist for physiology signals such as cardiac (ECG, PPG) or respiratory data. Many packages exist in Python to read these formats but they load into different data structures. This package is a wrapper of sorts for already existing tools providing a unified easy-to-use interface.



# Installation

```
python3 -m pip install biobabel
```

# Usage


## Command line

From the terminal or command prompt, you can use the following commands.
To show basic info about a file, use:

```
bioinfo <FILENAME>
```

To preview a file, use the provided script from the command line:

```
bioview <FILENAME>
```

Or, for a simpler lightweight viewer:

```
biobabel <FILENAME>
```

You can omit `<FILENAME>` in which case you will be prompted to select a file you want to preview.


## Python
Simple usage example in Python:

```
import biobabel
bio = biobabel.load('filename.txt')
bio.print()
bio.plot()
bio.save('new_filename.hdf5')
```

More complete overview of functionality in [Jupyter notebook](https://github.com/florisvanvugt/biobabel/blob/main/tests/Usage.ipynb).


# Requirements


# Physiology dialects

Currently supported dialects are:
* EDF through [PyEDFlib](https://pyedflib.readthedocs.io/en/latest/)
* labstreaminglayer (LSL) XDF (alpha) thanks to [pyxdf](https://pypi.org/project/pyxdf/)
* BioPAC Acknowledge (acq) thanks to [bioread](https://pypi.org/project/bioread/)
* opensignals ("OpenSignals (r)evolution" thanks to [opensignalsreader](https://github.com/PGomes92/opensignalsreader)
* Biosemi BDF thanks to [pybdf](https://pypi.org/project/pybdf/)
* Generic CSV (where CSV delimiter is automatically inferred and the time column is guessed as well)
* Brams-Bio-Box (in-house format, even though the Generic-CSV functionality should take care of this now)
* hdphysio5 thanks to [hdphysio5](https://github.com/florisvanvugt/hdphysio5)
* TeensyECG (in-house format)



# Development

Install latest development version from Github:

```
python -m pip install --upgrade "biobabel @ git+https://github.com/florisvanvugt/biobabel"
```


Install locally:

```
pip install .
```

and editable:

```
pip install -e .
```


