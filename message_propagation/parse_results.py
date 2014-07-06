import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import argparse
import re
from collections import defaultdict


matplotlib.rcParams['figure.figsize'] = 12, 12
matplotlib.rcParams['figure.dpi'] = 1200
matplotlib.rcParams['axes.labelsize'] = 20
matplotlib.rcParams['legend.fontsize'] = 20
matplotlib.rcParams['xtick.labelsize'] = 18
matplotlib.rcParams['ytick.labelsize'] = 18


def strip_trailing_slash(s):
    if s.endswith("/"):
        s = s[:-1]
    return s


def extract(rundir):
    raw = {
        "Tc": defaultdict(lambda: defaultdict(list)),
        "Rc": defaultdict(lambda: defaultdict(list))
    }
    for run in os.listdir(rundir):
        match = re.match("(Tc|Rc)-([a-z]+)-[0-9]+", run)
        if match:
            direction = match.group(1)
            mode = match.group(2)
            fd = open(rundir + run)
            u = 0
            for line in fd.readlines():
                raw[direction][mode][u].append(float(line))
                u += 1
            fd.close()
    return raw


def computeAverage(raw):
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

    return average, stdev

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testcase",
                        type=strip_trailing_slash,
                        nargs="?",
                        default=None,
                        help="path to the testcase directory")
    args = parser.parse_args()

    if args.testcase is not None:
        rundir = "{}/runs/".format(args.testcase)
        match = re.search("/([a-z0-9-]+)$", args.testcase)
        if not match:
            parser.error("Invalid testcase")
        else:
            network = match.group(0)

        raw = extract(rundir)
        average, stdev = computeAverage(raw)

        for direction in ["Tc", "Rc"]:
            for mode in average[direction]:
                itemlen = len(average[direction][mode])
                plt.errorbar(
                    range(itemlen),
                    average[direction][mode],
                    yerr=stdev[direction][mode],
                    ecolor="grey",
                    elinewidth=0.5)
            plt.xlabel("Nodes")
            plt.ylabel(r'$\bar{t_i}$')
            plt.xlim(xmax=itemlen)
            plt.ylim(0, 1.01)
            plt.legend(
                tuple(average[direction].keys()),
                "lower right")
            plt.axhline(1, color="grey", lw=0.5, ls="-.")
            plt.savefig("results/{0}/{0}-{1}.svg".format(
                network, direction))
            plt.clf()
    
    else:
        networks = ["ninux", "ffgraz", "ffwien"]
        networks_purged = ["ninux-w", "ffgraz-w", "ffwien-w",
                           "ninux-bet", "ffgraz-bet", "ffwien-bet"]
        average, stdev = {}, {}
        for network in networks + networks_purged:
            average[network], stdev[network] = computeAverage(
                extract("cases/{}/runs/".format(network)))
        modes = ["default", "mpr", "batman", "default-w", "default-bet"]
        for direction in ["Tc", "Rc"]:
            for mode in modes:
                suffix = None
                if mode.endswith("-w"):
                    suffix = "-w"
                    mode = "default"
                if mode.endswith("-bet"):
                    suffix = "-bet"
                    mode = "default"
                for network in networks:
                    if suffix is not None:
                        network += suffix
                    avg = average[network]
                    std = stdev[network]
                    itemlen = len(avg[direction][mode])
                    x = [float(i) * 100.0 / float(itemlen)
                         for i in range(itemlen)]
                    plt.errorbar(
                        x,
                        avg[direction][mode],
                        yerr=std[direction][mode],
                        ecolor="grey",
                        elinewidth=0.5)
                plt.xlabel("Nodes (%)")
                if direction == "Tc":
                    plt.ylabel(r"$t_i$")
                else:
                    plt.ylabel(r"$t'_i$")
                plt.ylim(0, 1.01)
                plt.xlim(0, 100)
                plt.legend(tuple(networks), "lower right")
                plt.axhline(1, color="grey", lw=0.5, ls="-.")
                if suffix is not None:
                    plt.savefig("results/all-{}{}-{}.svg".format(
                        mode, suffix, direction))
                else:
                    plt.savefig("results/all-{}-{}.svg".format(
                        mode, direction))
                plt.clf()
