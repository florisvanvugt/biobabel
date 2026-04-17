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

On Windows machines, some of the packages that `biobabel` depends on may require you to install Microsoft C++ Build Tools. If this is your case, when you run the above installation command, an error message will prompt you to install the build tools and includes a link from where you can download the tools. Re-run the biobabel installation after you have installed the build tools.



Basic usage
-----------

You would typically start by loading a physiology data file using the ``biobabel.load()`` function:

.. autofunction:: biobabel.load

Example:

>>> import biobabel as bb
>>> bio = bb.load('tests/example.hdf5')

		  
This loads the data into an object of the :ref:`biodata` class, the core of the Biobabel logic.



>>> bio.print()
>>> bio.plot()
>>> bio.save('tests/new_filename.hdf5')


More complete overview of functionality in [Jupyter notebook](https://github.com/florisvanvugt/biobabel/blob/main/tests/Usage.ipynb).


	       

   
