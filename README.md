

# What is this

Many different file formats exist for physiology signals such as cardiac (ECG, PPG) or respiratory data. Many packages exist in Python to read these formats but they load into different data structures. This package is a wrapper of sorts for already existing tools providing a unified easy-to-use interface.



# Installation

```
python -m pip install 'biobabel @ git+https://github.com/florisvanvugt/biobabel'
```

# Usage


Simple usage example in Python:

```
import biobabel
bio = biobabel.load('filename.txt')
bio.print()
bio.plot()
bio.save('new_filename.hdf5')
```




# Requirements


# Physiology dialects

Currently supported dialects are:
* TeensyECG (custom)
* hdphysio5 thanks to [hdphysio5](https://github.com/florisvanvugt/hdphysio5)
* labstreaminglayer (LSL) XDF (rudimentary) thanks to [pyxdf](https://pypi.org/project/pyxdf/)
* BioPAC Acknowledge (acq) thanks to [bioread](https://pypi.org/project/bioread/)
* opensignals ("OpenSignals (r)evolution" thanks to [opensignalsreader](https://github.com/PGomes92/opensignalsreader)

Wish-list:
* EDF


# Development

Install locally:

```
pip install .
```

and editable:

```
pip install -e .
```



Create wheels with:

```
python3 -m build
```


