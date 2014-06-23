import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import re
from collections import defaultdict


def strip_trailing_slash(s):
    if s.endswith("/"):
        s = s[:-1]
    return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testcase",
                        type=strip_trailing_slash,
                        help="path to the testcase directory")
    args = parser.parse_args()
    rundir = "{}/runs/".format(args.testcase)

    raw = {
        "T": defaultdict(lambda: defaultdict(list)),
        "R": defaultdict(lambda: defaultdict(list)),
        "Tc": defaultdict(lambda: defaultdict(list)),
        "Rc": defaultdict(lambda: defaultdict(list))
    }
    for run in os.listdir(rundir):
        match = re.match("(Tc?|Rc?)-([a-z]+)-[0-9]+", run)
        if match:
            direction = match.group(1)
            mode = match.group(2)
            fd = open(rundir + run)
            u = 0
            for line in fd.readlines():
                raw[direction][mode][u].append(float(line))
                u += 1
            fd.close()

    average = {}
    stdev = {}
    for direction in raw.keys():
        average[direction] = defaultdict(lambda: np.array([]))
        stdev[direction] = defaultdict(lambda: np.array([]))
        for mode in raw[direction].keys():
            average[direction][mode] = np.array(
                [np.average(ulist) for ulist in raw[direction][mode].values()]
            )
            stdev[direction][mode] = np.copy(average[direction][mode])
            for i in average[direction][mode].argsort():
                stdev[direction][mode][i] = np.std(raw[direction][mode][i])
            average[direction][mode].sort()

    for probname in ["T", "R"]:
        countname = probname + "c"
        prob = average[probname]
        count = average[countname]
        for mname in prob:
            itemlen = len(prob[mname])
            probLine = plt.errorbar(
                range(itemlen), prob[mname],
                yerr=stdev[probname][mname],
                ecolor='grey')
            countLine = plt.errorbar(
                range(itemlen), count[mname],
                yerr=stdev[countname][mname],
                ecolor='grey')
            plt.ylim(0, 1)
            plt.xlabel("Nodes")
            plt.ylabel("{0}, {0}c".format(probname))
            plt.figlegend(
                (probLine, countLine),
                (probname, countname),
                "lower right"
            )
            plt.savefig("{}/{}-{}.png".format(args.testcase, probname, mname))
            plt.clf()
