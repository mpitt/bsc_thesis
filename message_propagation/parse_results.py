import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import re
from collections import defaultdict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testcase",
                        help="path to the testcase directory")
    args = parser.parse_args()

    raw = {
        "T": defaultdict(lambda: defaultdict(list)),
        "R": defaultdict(lambda: defaultdict(list))
    }
    for run in os.listdir(args.testcase):
        match = re.match("(T|R)-([a-z]+)-[0-9]+", run)
        if match:
            direction = match.group(1)
            mode = match.group(2)
            fd = open(args.testcase + run)
            u = 0
            for line in fd.readlines():
                raw[direction][mode][u].append(float(line))
                u += 1
            fd.close()

    average = {
        "T": defaultdict(lambda: np.array([])),
        "R": defaultdict(lambda: np.array([]))
    }
    stdev = {
        "T": defaultdict(lambda: np.array([])),
        "R": defaultdict(lambda: np.array([]))
    }
    for direction in raw.keys():
        for mode in raw[direction].keys():
            average[direction][mode] = np.array(
                [np.average(ulist) for ulist in raw[direction][mode].values()]
            )
            stdev[direction][mode] = np.copy(average[direction][mode])
            for i in average[direction][mode].argsort():
                stdev[direction][mode][i] = np.std(raw[direction][mode][i])
            average[direction][mode].sort()

    for dname, direction in average.items():
        for mname, mode in direction.items():
            plt.errorbar(
                range(len(mode)), mode,
                yerr=stdev[dname][mname],
                ecolor='grey')
            plt.ylim(0, max(mode))
            plt.savefig(args.testcase + dname + "-" + mname + ".png")
            plt.clf()
