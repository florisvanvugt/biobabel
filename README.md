


# Installation

```
python -m pip install 'biobabel @ git+https://github.com/florisvanvugt/biobabel'
```

# Usage

In Python:

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
* hdphysio5 https://github.com/florisvanvugt/hdphysio5
* labstreaminglayer (LSL) XDF (rudimentary)

Wish-list:
* OpenSignals
* XDF
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


