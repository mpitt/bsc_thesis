import networkx as nx
from scipy import stats
import sys, os, argparse

if __name__ == '__main__':
    generators = {
            'random': nx.fast_gnp_random_graph,
            'path': nx.path_graph,
            'complete': nx.complete_graph
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("generator", choices=generators.keys())
    parser.add_argument("-n", "--nodes", type=int, required=True)
    parser.add_argument("-p", "--gnpp", type=float)
    parser.add_argument("-w", "--maxweight", type=float, default=0.2,
            help="Maximum probability of loss, default 0.2")
    parser.add_argument("name")
    args = parser.parse_args()

    gen = args.generator
    if gen == 'random':
        if args.gnpp == None:
            print "Error: -p is required with the random generator"
            sys.exit(2)
        g = generators[gen](args.nodes, args.gnpp)
        while(len(nx.connected_components(g)) > 1):
            g = generators[gen](args.nodes, args.gnpp)
    else:
        g = generator[gen](args.nodes)

    dist = stats.uniform(0,args.maxweight)
    for e in g.edges_iter():
        g[e[0]][e[1]]['weight'] = dist.rvs()
    os.mkdir("cases/"+args.name)
    nx.write_gpickle(g, "cases/"+args.name+"/graph.pickle")
    f = open("cases/"+args.name+"/info", "w")
    f.write("Number of nodes: ")
    f.write(str(len(g))+"\n")
    f.write("Number of edges: ")
    f.write(str(g.number_of_edges())+"\n")
    f.write("Density: "+str(nx.density(g))+"\n")
    f.close()
    f = open("cases/"+args.name+"/weights", "w")
    for e in g.edges_iter(data=True):
        f.write(str(e[2]['weight'])+"\n")
    f.close()
