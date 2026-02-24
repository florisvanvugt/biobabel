

# Biobabel : a unified interface for reading a plethora of physiology file formats

[![DOI](https://zenodo.org/badge/660740111.svg)](https://zenodo.org/badge/latestdoi/660740111)


Many different file formats exist for physiology signals such as cardiac (ECG, PPG) or respiratory data. Many packages exist in Python to read these formats but they load into different data structures. This package is a wrapper of sorts for already existing tools providing a unified easy-to-use interface.




# Installation

```
python3 -m pip install biobabel
```

Install latest development version from Github:

```
python -m pip install --upgrade "biobabel @ git+https://github.com/florisvanvugt/biobabel"
```



# Documentation

https://biobabel.readthedocs.io/




# Physiology dialects

Currently supported dialects for reading are:
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

Install locally:

```
pip install .
```

and editable:

```
pip install -e .
```


# Testing

To run the included tests, simply install the package and then run the following command from the root:

```
pytest
```



# Citation

Please cite this work if you use it:

  * van Vugt, F.T. (2025). Biobabel: Python package for reading major bio/physiology data formats. https://doi.org/10.5281/zenodo.15453402
  
Thank you!
