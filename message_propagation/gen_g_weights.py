import networkx as nx
import numpy as np
from scipy.stats import uniform
import sys
import os
import argparse

if __name__ == '__main__':
    generators = {
        'random': nx.fast_gnp_random_graph,
        'ba': nx.barabasi_albert_graph,
        'path': nx.path_graph,
        'complete': nx.complete_graph
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("generator", choices=generators.keys())
    parser.add_argument("-n", "--nodes", type=int, required=True)
    parser.add_argument("-p", "--gnpp", type=float)
    parser.add_argument("-m", "--edges", type=int)
    parser.add_argument(
        "-w",
        "--maxweight", type=float,
        default=0.2,
        help="Maximum probability of loss, default 0.2")
    parser.add_argument("name")
    args = parser.parse_args()

    gen = args.generator
    if gen == 'random':
        if args.gnpp is None:
            print "Error: -p is required with the random generator"
            sys.exit(2)
        g = generators[gen](args.nodes, args.gnpp)
        while(len(nx.connected_components(g)) > 1):
            g = generators[gen](args.nodes, args.gnpp)
    elif gen == 'ba':
        if args.edges is None:
            print "Error: -m is required with the Barabasi-Albert generator"
            sys.exit(2)
        g = generators[gen](args.nodes, args.edges)
    else:
        g = generators[gen](args.nodes)

    dist = uniform(0, args.maxweight)
    for u, v in g.edges_iter():
        g[u][v]['weight'] = dist.rvs()
    os.mkdir("cases/" + args.name)
    nx.write_gpickle(g, "cases/" + args.name + "/graph.pickle")
    f = open("cases/" + args.name + "/info", "w")
    f.write("Number of nodes: ")
    f.write(str(len(g)) + "\n")
    f.write("Number of edges: ")
    f.write(str(g.number_of_edges()) + "\n")
    f.write("Average degree: %8.4f\n" % np.average(g.degree().values()))
    weights = [float(attr['weight']) for u, v, attr in g.edges_iter(data=True)]
    f.write("Weights (min/avg/max/std): %f/%f/%f/%f\n" % (
            min(weights), np.average(weights), max(weights),
            np.std(weights, dtype=np.float64)))
    f.close()
    f = open("cases/" + args.name + "/weights", "w")
    for w in weights:
        f.write("%f\n" % w)
    f.close()
