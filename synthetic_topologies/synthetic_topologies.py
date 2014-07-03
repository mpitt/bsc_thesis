import os
import time
import errno
import cPickle as pk
from collections import defaultdict
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['figure.figsize'] = 12, 12 
matplotlib.rcParams['figure.dpi'] = 1200
matplotlib.rcParams['axes.labelsize'] = 20
matplotlib.rcParams['legend.fontsize'] = 20
matplotlib.rcParams['xtick.labelsize'] = 18
matplotlib.rcParams['ytick.labelsize'] = 18
matplotlib.rcParams['svg.fonttype'] = 'none'
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
# from scipy import optimize
import random
from string import split

resultDir = "results/" + time.strftime("%Y%m%d-%H%M")  # 20141225-1453
numtests = 30
nodes = 150
gnp_random_p = 0.03
barabasi_m = 2

verbose = 2  # [3:debug|2:info|1:warning|0:error]
graphModes = "all"  # [all|e-r|b-a|known]


class dataParser():
    strategyRemove = ""
    strategyOrder = ""
    degDist = False

    def __init__(self, strategy, queue):
        self.degDist = (strategy == "degdist")
        if (not self.degDist):
            self.strategyRemove, self.strategyOrder = split(strategy, "_")
        self.q = queue

    def run(self, data):
        self.data = data
        if self.degDist:
            self.getDegreeDistribution()
        else:
            self.getRobustness()

    def getDegreeDistribution(self):
        degreeDistribution = defaultdict(float)
        samples = 0.0
        for G in self.data:
            for node in G:
                degreeDistribution[G.degree(node)] += 1
                samples += 1
        ycount = [d / len(self.data) for d in degreeDistribution.values()]
        for d in degreeDistribution:
            degreeDistribution[d] /= samples
        x = degreeDistribution.keys()
        y = degreeDistribution.values()

        # fitfunc = lambda p, x: p[0] * x ** (p[1])
        # errfunc = lambda p, x, y: (y - fitfunc(p, x))

        # out, success = optimize.leastsq(
        #     errfunc,
        #     [1, -1],
        #     args=(x, y)
        # )
        #fittedValue = [out[0] * (v ** out[1]) for v in x]
        q.put({"x": x, "y": y, "ycount": ycount})
  
    def getRobustness(self):
        avgRobustness = defaultdict(list)
        for G in self.data:
            if self.strategyRemove == "nodes":
                initial = len(G.nodes())
            else:
                initial = len(G.edges())
            r = self.computeRobustness(
                G,
                tests=30,
                remove=self.strategyRemove,
                order=self.strategyOrder)[0]
            for k, v in r.items():
                percent = int(100 * float(k) / initial)
                avgRobustness[percent].append(v)

        confidence = [self.conf_interval_95(v) for v in avgRobustness.values()]
      
        retval = {}
        retval["x"] = avgRobustness.keys()
        retval["y"] = [
            np.average(avgRobustness[k]) for k in sorted(avgRobustness.keys())]
        retval["CI"] = confidence
        q.put(retval)

    def computeRobustness(
        self,
        graph,
        tests=100,
        remove="nodes",
        order="random"
    ):

        if remove == "nodes":
            if order == "random":
                items = graph.nodes()
            elif order == "deg":
                d = graph.degree()
                items = sorted(d, key=d.get, reverse=True)
            elif order == "bet":
                betweenness = nx.betweenness_centrality(graph)
                items = sorted(betweenness, key=betweenness.get, reverse=True)
            elif order == "close":
                closeness = nx.closeness_centrality(graph)
                items = sorted(closeness, key=closeness.get, reverse=True)
            elif order == "cluster":
                T = nx.triangles(graph)
                d = graph.degree()
                # The clustering coefficient is (2*T[n])/((d[n])(d[n]-1))
                # so the d/c ratio is (2*t[n])/(d[n]-1)
                DCratio = defaultdict(list)
                for n in graph.nodes():
                    if d[n] < 2:
                        DCratio[n] = 0
                    else:
                        DCratio[n] = (2 * T[n]) / (d[n] - 1)
                items = sorted(graph.nodes(),
                               key=lambda n: DCratio[n], reverse=True)
            else:
                print "=== ERROR, order not valid"
                return
        else:
            if order == "random":
                items = graph.edges()
            elif order == "bet":
                betweenness = nx.edge_betweenness_centrality(graph)
                items = sorted(betweenness, key=betweenness.get, reverse=True)
            else:
                print "=== ERROR, order not valid"
                return

        itemlen = len(items)
        nlen = float(len(graph.nodes()))
        mainCSize = defaultdict(list)
        mainNonCSize = defaultdict(list)
        fractionToRemove = 0.4
        for i in range(tests):
            if order == "random":
                random.shuffle(items)
            purgedGraph = graph.copy()
            for k in range(int(itemlen * fractionToRemove)):
                if remove == "nodes":
                    purgedGraph.remove_node(items[k])
                else:
                    purgedGraph.remove_edge(*items[k])
                compList = nx.connected_components(purgedGraph)
                mainCSize[k].append(float(len(compList[0])) / nlen)
                compSizes = [len(r) for r in compList[1:]]
                if len(compSizes) == 0:
                    mainNonCSize[k].append(0)
                else:
                    mainNonCSize[k].append(np.average(compSizes) / itemlen)

        mainCSizeAvg = {}
        for k, tests in mainCSize.items():
            mainCSizeAvg[k] = np.mean(tests)
        return mainCSizeAvg, mainNonCSize

    def conf_interval_95(self, data):
        n = len(data)
        sdev = np.std(data)
        serr = sdev / np.sqrt(n)
        return 1.96 * serr


class dataPlot:

    def __init__(self, C=None):
        self.x = []
        self.y = []
        self.yCI = []
        self.series_labels = []
        self.title = ""
        self.xAxisLabel = ""
        self.yAxisLabel = ""
        self.xright = None
        self.outFile = ""
        self.key = []
        self.legendPosition = "center right"
        if C is None:
            self.fileType = ".svg"
        else:
            self.fileType = "." + C.imageExtension

    def plotData(self, style="-"):
        if self.outFile == "":
            return
        dataDimension = 0
        ax = plt.subplot(111)
        for i in self.y:
            l = self.series_labels[dataDimension]
            y = self.y[dataDimension]
            x = self.x[dataDimension]
            kwargs = {'label': l}
            if self.yCI != []:
                ci = self.yCI[dataDimension]
                ax.errorbar(x, y, yerr=ci, fmt=style, **kwargs)
            else:
                ax.loglog(x, y, style, **kwargs)
            dataDimension += 1
        if self.xright is not None:
            ax.set_xlim(right=self.xright)
        plt.title(self.title)
        plt.xlabel(self.xAxisLabel)
        plt.ylabel(self.yAxisLabel)
        if self.legendPosition == "aside":
            box = ax.get_position()
            ax.set_position([box.x0,
                             box.y0,
                             box.width * 0.8,
                             box.height])
            ax.legend(loc="center left", fancybox=True, 
                      bbox_to_anchor=(1, 0.5), shadow=True, 
                      prop={'size': 15}, numpoints=1)
        else: 
            plt.legend(
                loc=self.legendPosition,
                fancybox=True, 
                shadow=True,
                numpoints=1
            )
        plt.savefig(self.outFile + self.fileType)
        plt.clf()


def createResultDir(name):
    c = 0
    retry = True
    while retry:
        retry = False
        try:
            os.mkdir(name)
        except OSError as e:
            if e.errno == errno.EEXIST:
                name = name + "-" + c
                retry = True
            else:
                raise
        c += 1


def getGraphModeStats(graphs):
    l = len(graphs)
    n = 0
    m = 0
    for g in graphs:
        n += len(g)
        m += len(g.edges())
    return n / l, m / l

 
if __name__ == "__main__":
    createResultDir(resultDir)
    graphs = {}
    if graphModes == "all" or graphModes == "e-r":
        graphs["e-r"] = []
        for test in range(numtests):
            graphs["e-r"].append(
                nx.fast_gnp_random_graph(nodes, p=gnp_random_p))
    if graphModes == "all" or graphModes == "b-a":
        graphs["b-a"] = []
        for test in range(numtests):
            graphs["b-a"].append(
                nx.barabasi_albert_graph(nodes, m=barabasi_m))
    if graphModes == "wcn" or graphModes == "all":
        try:
            f = open("../simpleCN-50.pickle")
        except IOError:
            print("file ../simpleCN-50.pickle")
            raise
        else:
            graphs.update(pk.load(f))
            f.close()
    if graphModes == "known":
        try:
            f = open("known.pickle")
        except IOError:
            print("File not found")
        else:
            graphs = pk.load(f)
            f.close()
    statfile = open(resultDir + "/stat.txt", "w")
    for mode, cases in graphs.items():
        statfile.write(mode + " graphs: ")
        nodes, edges = getGraphModeStats(cases)
        avgDeg = 2.0 * float(edges) / float(nodes)
        statfile.write(str(nodes) + " nodes, ")
        statfile.write(str(edges) + " edges, ")
        statfile.write("<k> = " + str(avgDeg))
        statfile.write("\n")
    
    strategies = [
        'degdist'  #,
        # 'nodes_random',
        # 'nodes_deg',
        # 'nodes_bet',
        # 'nodes_close'
    ]
#    if nodeStrategy == "all":
#        for s in ["random", "deg", "bet", "close", "cluster"]:
#            strategies.append("nodes_"+s)
#    elif nodeStrategy != "none":
#        strategies.append("nodes_"+nodeStrategy)
# 
#    if linkStrategy == "all":
#        for s in ["random", "bet"]:
#            strategies.append("links_"+s)
#    elif linkStrategy != "none":
#        strategies.append("links_"+linkStrategy)
  
    if verbose >= 2:
        print "Graph modes"
        print graphs.keys()
        print "Strategies: "
        print strategies
    if verbose >= 3:
        print "e-r graphs (nodes, links): "
        print [(len(G.nodes()), len(G.edges())) for G in graphs["e-r"]]
        print "Preferential attachment graphs (nodes, links): "
        print [(len(G.nodes()), len(G.edges())) for G in graphs["b-a"]]
  
    parsers = []
    for s in strategies:
        for mode in graphs:
            q = Queue()
            parser = dataParser(s, q)
            p = Process(target=parser.run, kwargs={"data": graphs[mode]})
            parsers.append((s, mode, p, q))
            p.start()
  
    retValues = defaultdict(dict)
    while True:
        alive = len(parsers)
        for (s, m, p, q) in parsers:
            if not q.empty():
                retValues[s][m] = q.get()
                print "Subprocess ",\
                    s, " ", m, " exited"
            if not p.is_alive():
                alive -= 1
    
        if alive == 0:
            break
  
    time.sleep(1)
    for s in retValues:
        val = retValues[s]
        plot = dataPlot()
        for mode in graphs:
            if mode in val:
                plot.series_labels.append(mode)
                plot.x.append(val[mode]["x"])
                plot.y.append(val[mode]["y"])
        if s == "degdist":
            x = np.arange(50)
            y = x ** -2.0
            plot.x.append(x)
            plot.y.append(y)
            plot.series_labels.append(r'$k^{-2}$')
            plot.title = "Degree distribution"
            plot.xAxisLabel = "Degree"
            plot.yAxisLabel = "Frequency"
            plot.legendPosition = "center right"
            plot.outFile = resultDir + "/degree_distribution"
            # plot.plotData(style="o:")
            plot.plotData()
        else:
            for mode in graphs:
                if mode in val:
                    plot.yCI.append(val[mode]["CI"])
            plot.title = "Robustness metrics with " + s
            plot.xAxisLabel = "Fraction of failed links/nodes"
            plot.yAxisLabel = "Main cluster size / initial size"
            plot.legendPosition = "lower left"
            plot.outFile = resultDir + "/" + s + "_robustness"
            plot.plotData(style="o:")

    for s, val in retValues.items():
        with open("{}/{}.txt".format(resultDir, s), "w+") as f:
            if s == "degdist":
                title = " Degree "
                ls = {}
                ls["x"] = len(title)
                sep = "{0:-<{l}}".format("-", l=ls["x"])
                for mode in val:
                    ls[mode] = max([8, len(mode)])
                    title += " {:>{l}}".format(mode, l=ls[mode])
                    sep += " {0:-<{l}}".format("-", l=ls[mode])
                f.write("{}\n{}\n".format(title, sep))
                points = max([len(val[mode]["x"]) for mode in val])
                x = [val[mode]["x"] for mode in val][0]
                for i in range(points):
                    raw = "{0:>{l}}".format(i + 1, l=ls["x"])
                    for mode in val:
                        try:
                            yi = val[mode]["ycount"][i]
                        except IndexError:
                            yi = 0.0
                        raw += " {0:>{l}.2f}".format(yi, l=ls[mode])
                    f.write("{}\n".format(raw))

