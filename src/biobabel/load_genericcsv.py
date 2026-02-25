import biobabel
import numpy as np
import os
import datetime
import pandas as pd


#
#
#
# Module for loading generic CSV
#
#   Basically what we try to do is guess as much as possible.
#
#


def guess_time_column(dat):
    # Given a table with some columns, guess which one might be the time column
    # Return the name of the column, and time divider
    for col in dat.columns:

        # See if this could be a time column
        vals = dat[col]
        ds = np.diff(vals)

        # Check : values need to be increasing
        if not min(ds) > 0:
            continue

        # Check : values need to increase by roughly the same amount each time
        cv = np.std(ds) / np.mean(ds)
        if cv > 0.1:
            continue

        # If we get this far it's looking pretty good!
        print("Guessed '{}' is the time column.".format(col))
        return col, 1000  # assume ms as default sampling unit

    return None, 1


def load(fname):
    """Load a file with CSV format."""

    print("Generic CSV load")

    bio = biobabel.Biodata()  # create a new biodata object
    bio.name = fname

    m_time = os.path.getmtime(fname)
    dt_m = datetime.datetime.fromtimestamp(m_time)
    bio.meta["date"] = dt_m.strftime(biobabel.DATEFORMAT)

    ## gb['renames'] comes from the file configuration
    tab = pd.read_csv(
        fname, sep=None, engine="python"
    )  # pandas will try to guess the delimiter, this might fail!

    tcol, TIME_DIVIDER = guess_time_column(tab)
    if tcol:

        tab[tcol] = tab[tcol] / TIME_DIVIDER  # express in s
        tdur = max(tab[tcol]) - min(tab[tcol])
        dt = np.diff(tab[tcol])
        mediandt = np.median(dt)
        print("-- A human may want to inspect this:")
        print(
            "Time step values (in s) min={:.5f}, max={:.5f}, mean={:.5f}, median={:.5f}, SD={:.5f}".format(
                np.min(dt), np.max(dt), np.mean(dt), mediandt, np.std(dt)
            )
        )
        THRESH = mediandt * 1.1
        print("# of time steps >.{}: {}".format(THRESH, np.sum(dt > THRESH)))
        print("----")
        print()

    else:
        # Create some defaults
        TIME_DIVIDER = 1000  # assume time units by default are in ms
        tcol = "__t__"  # create a time column
        tab[tcol] = np.arange(tab.shape[0])
        mediandt = 1

    SR = 1 / mediandt

    participant = "participant"

    for col in tab.columns:
        nm = col.lower()

        if nm == "t":
            continue

        hdr = {
            "id": col,
            "participant": participant,
            "sampling_frequency": SR,
            "modality": biobabel.guess_modality(nm),
            "units": "V",
        }
        data = 3.3 * (np.array(tab[col]) / 1023)
        bio.add_channel((hdr, data))

    return bio
