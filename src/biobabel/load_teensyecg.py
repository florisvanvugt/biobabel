import biobabel
import numpy as np
import os
import datetime
import json


def load(fname):

    bio = biobabel.Biodata()  # create a new biodata object
    bio.name = fname

    m_time = os.path.getmtime(fname)
    dt_m = datetime.datetime.fromtimestamp(m_time)
    bio.add_meta("date", dt_m.strftime(biobabel.DATEFORMAT))

    with open(fname, "r") as f:
        firstline = f.readline()
        # print(firstline)
        cont = f.read()

    # See if we can scrape more config data
    cfg = firstline.find("CONFIG")
    if cfg > -1:
        c = firstline[(cfg + 6) :]
        # print(c)
        config = json.loads(c)
        # print(config)
        for k in config:
            bio.add_meta(k, config[k])

    # Remove some initial nonsense data that typically enters these files
    startp = cont.find("# Start signal received")
    if startp < 0:
        print("### ERROR, no starting point found!")

    contents = cont[startp:].split("\n")

    # Assumed unless ohterwise specified
    TIME_DIVISOR = 1000

    # TODO: could retrieve the field names from the data header itself

    alldata = []
    events = []
    for ln in contents:
        if not ln:
            continue
        items = ln.split(" ")
        if items[1] == "#":
            ev = {"type": items[3], "t": int(items[4])}
            events.append(ev)
            continue
        if items[1] == "0" and items[2] == "raw":
            # Try to parse it
            t, fsr, ecg, therm, ppg, snd = items[3:]
            alldata.append(
                {
                    "t": int(t),
                    "fsr": int(fsr),
                    "ecg": int(ecg),
                    "therm": int(therm),
                    "ppg": int(ppg),
                    "snd": int(snd),
                }
            )

    t = [d["t"] for d in alldata]
    t0 = min(t)
    dt = np.diff(t) / TIME_DIVISOR

    mediandt = np.median(dt)

    print("-- A human may want to inspect this:")
    print(
        "Time step values (in s) min={:.5f}, max={:.5f}, mean={:.5f}, median={:.5f}, SD={:.5f}".format(
            np.min(dt), np.max(dt), np.mean(dt), np.median(dt), np.std(dt)
        )
    )
    THRESH = mediandt * 1.1
    print("# of time steps >.{}: {}".format(THRESH, np.sum(dt > THRESH)))
    print("----")
    print()

    SR = 1 / mediandt

    for chan in ["fsr", "ecg", "therm", "ppg", "snd"]:
        hdr = {
            "id": chan,
            "participant": "participant",
            "sampling_frequency": SR,
            "modality": biobabel.guess_modality(chan),
            "units": "a.u",
        }
        dat = [d[chan] for d in alldata]
        bio.add_channel((hdr, np.array(dat)))

    eventtypes = list(set([x["type"] for x in events]))
    markers = {}
    for e in eventtypes:
        markers[e] = [(ev["t"] - t0) / TIME_DIVISOR for ev in events if ev["type"] == e]
    bio.markers = markers

    return bio
