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
        "T": defaultdict(list),
        "R": defaultdict(list)
    }
    for direction in raw.keys():
        for mode in raw[direction].keys():
            average[direction][mode] = \
                [np.average(ulist) for ulist in raw[direction][mode].values()]

    print average
    for dname, direction in average.items():
        for mname, mode in direction.items():
            plt.hist(mode, bins=50, normed=True)
            plt.savefig(args.testcase + dname + "-" + mname + ".png")
            plt.clf()
