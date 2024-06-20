Usage
=====

.. _installation:

Installation
------------

To use Biobabel, first install it using pip:

.. code-block:: console

   $ pip install biobabel


Or you can install the latest development version directly from Github:
   
.. code-block:: console

   $ python -m pip install --upgrade "biobabel @ git+https://github.com/florisvanvugt/biobabel"


In both cases, omit the dollar sign when you copy-paste this into the terminal.



Basic usage
-----------

You would typically start by loading a physiology data file using the ``biobabel.load()`` function:

.. autofunction:: biobabel.load

Example:

>>> import biobabel as bb
>>> bb.load('tests/example.hdf5')

		  
This loads the data into an object of the :ref:`biodata` class, the core of the Biobabel logic.

.. autoclass:: biobabel.Biodata
   :no-index:

   
	       

   
