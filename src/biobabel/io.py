import biobabel.load_teensyecg
import biobabel.load_hdphysio5
import biobabel.load_lsl
import biobabel.load_acq
import biobabel.load_opensignals
import biobabel.load_bramsbiobox
import biobabel.load_genericcsv
import biobabel.load_bdf
import biobabel.load_edf

import os


def load(fname, dialect=None):
    """
    Load physiology signal file.

    fname : filename of the file to be read
    dialect : the file format. If None, the format is guessed
    """

    if not os.path.exists(fname):
        print("File '{}' does not seem to exist.".format(fname))
        return

    if dialect == None:
        # Try to guess
        dialect = guess_dialect(fname)
        if dialect:
            print("Guessed that this is {} format.".format(dialect))

    if dialect == "teensyecg":
        return biobabel.load_teensyecg.load(fname)

    if dialect == "hdphysio5":
        return biobabel.load_hdphysio5.load(fname)

    if dialect == "lsl":
        return biobabel.load_lsl.load(fname)

    if dialect == "acq":
        return biobabel.load_acq.load(fname)

    if dialect == "opensignals":
        return biobabel.load_opensignals.load(fname)

    if dialect == "csv":
        return biobabel.load_genericcsv.load(fname)

    if dialect == "bdf":
        return biobabel.load_bdf.load(fname)

    if dialect == "edf":
        return biobabel.load_edf.load(fname)

    if dialect == "bramsbiobox":
        return biobabel.load_bramsbiobox.load(fname)

    return None  # did not manage to load


def get_compatible_file_types():
    """Return a list of supported file types
    that can be fed to the open file dialog."""
    ftps = [
        ("Biopac Acqknowledge (ACQ)", ".acq"),
        ("Extensible Data Format (XDF)", ".xdf"),
        ("HDPhysio5 (HDF5)", ".hdf5"),
        ("European Data Format (EDF)", ".edf"),
        ("Comma-separated values (CSV)", ".csv"),
        ("Text file (TXT)", ".txt"),
    ]
    return [
        ("All biobabel compatible file types", " ".join([ext for (_, ext) in ftps]))
    ] + ftps


def guess_dialect(fname):

    if fname.lower().endswith(".bdf"):
        return "bdf"  # guess
    if fname.lower().endswith(".hdf5"):
        return "hdphysio5"  # guess
    if fname.lower().endswith(".xdf"):
        return "lsl"  # guess
    if fname.lower().endswith(".edf"):
        return "edf"  # guess
    if fname.lower().endswith(".acq"):
        return "acq"  # guess

    if fname.lower().endswith(".txt"):

        # To guess the dialect, we have to actually probe the file itself
        with open(fname) as f:
            ln = f.readline()

        if ln.find("OpenSignals") > -1:
            return "opensignals"

        return "teensyecg"  # probably best to try

    if fname.lower().endswith(".csv"):

        # To guess the dialect, we have to actually probe the file itself
        with open(fname) as f:
            ln = f.readline().lower()

        if (
            ln.find("time(ms)") > -1
            and ln.find("xaccel") > -1
            and ln.find("gauge") > -1
        ):
            return "bramsbiobox"

        else:
            return "csv"  # generic CSV

    return "csv"  # default is generic CSV
