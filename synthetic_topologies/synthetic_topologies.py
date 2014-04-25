import sys, os, time
import cPickle as pk
from collections import defaultdict
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['figure.figsize'] = 12, 12 
matplotlib.rcParams['figure.dpi'] = 1200
import matplotlib.pyplot as plt
from matplotlib import rcParams
from multiprocessing import Process, Queue
from scipy import stats, optimize
import random
from string import split
import pdb

resultDir = "results/"+time.strftime("%Y%m%d-%H%M") # 20141225-1453
numtests = 30
nodes = 500
gnp_random_p = 0.02
barabasi_m = 2

verbose = 2 # [3:debug|2:info|1:warning|0:error] 
graphModes = "known" # [all|random|pref_att|known]
#nodeStrategy = "random" # [all|random|deg|bet|close|cluster|none]
#linkStrategy = "none" # [all|random|bet|none]

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
        print "Subprocess starting, removing "+\
            self.strategyRemove+\
            " in order of "\
            + self.strategyOrder
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
        for d in degreeDistribution:
            degreeDistribution[d] /= samples
        x = degreeDistribution.keys()
        y = degreeDistribution.values()

        fitfunc = lambda p, x: p[0] * x ** (p[1])
        errfunc = lambda p, x, y: (y - fitfunc(p,x))

        out,success = optimize.leastsq(
                errfunc,
                [1,-1],
                args=(x,y)
                )
        fittedValue = [out[0]*(v**out[1]) for v in x]
        q.put({"x": x, "y": y})
  
    def getRobustness(self):
        avgRobustness = defaultdict(list)
        for G in self.data:
            if self.strategyRemove == "nodes":
                initial = len(G.nodes())
            else:
                initial = len (G.edges())
            r = self.computeRobustness(
                G,
                tests=30,
                remove=self.strategyRemove,
                order=self.strategyOrder)[0]
        for k,v in r.items():
            percent = int(100*float(k)/initial)
            avgRobustness[percent].append(v)
      
        retval = {}
        retval["x"] = avgRobustness.keys()
        retval["y"] = \
            [np.average(avgRobustness[k]) for k in sorted(avgRobustness.keys())]
        q.put(retval)

    def computeRobustness(self, graph, tests=100, remove="nodes", order="random"):

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
                        DCratio[n] = (2*T[n])/(d[n]-1)
                items = sorted(graph.nodes(), key=lambda n: DCratio[n], reverse=True)
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
        for i in range(tests):
            if order == "random":
                random.shuffle(items)
            purgedGraph = graph.copy()
            for k in range(int(itemlen*0.8)):
                if remove == "nodes":
                    purgedGraph.remove_node(items[k])
                else:
                    purgedGraph.remove_edge(*items[k])
                compList =  nx.connected_components(purgedGraph)
                mainCSize[k].append(float(len(compList[0]))/nlen)
                compSizes = [len(r) for r in compList[1:]]
                if len(compSizes) == 0:
                    mainNonCSize[k].append(0)
                else:
                    mainNonCSize[k].append(np.average(compSizes)/itemlen)

        mainCSizeAvg = {}
        for k, tests in mainCSize.items():
            mainCSizeAvg[k] = np.average(tests)
        return mainCSizeAvg, mainNonCSize

class dataPlot:

    def __init__(self, C=None):
        self.x = []
        self.y = []
        self.title = ""
        self.xAxisLabel = ""
        self.yAxisLabel = ""
        self.outFile = ""
        self.key = []
        self.legendPosition = "center right"
        if C == None:
            self.fileType = ".png"
        else:
            self.fileType = "."+C.imageExtension

    def plotData(self, style = "-"):
        if self.outFile == "":
            return
        dataDimension = 0
        ax = plt.subplot(111)
        for y in self.y:
            l = self.y[dataDimension][1]
            v = self.y[dataDimension][0]
            if l != "": 
                ax.plot(self.x[dataDimension],
                    v, style, label=l)
            else :
                ax.plot(self.x[dataDimension], v, style)
            dataDimension += 1
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
                prop={'size':15}, numpoints=1)
        else: 
            plt.legend(
                loc=self.legendPosition,
                fancybox=True, 
                shadow=True,
                numpoints=1
            )
        plt.savefig(self.outFile+self.fileType)
        plt.clf()

if __name__  == "__main__":
    os.mkdir(resultDir)
    f = open(resultDir+"/options.txt", "w")
    f.write("Graph dimension: "+str(nodes)+" nodes, "+str(numtests)+" graphs per topology\n")
    f.write("Random generator, p="+str(gnp_random_p)+"\n")
    f.write("Barabasi generator, m="+str(barabasi_m))
    graphs = {}
    if graphModes == "all" or graphModes == "random":
        graphs["random"] = []
        for test in range(numtests):
            graphs["random"].append(nx.fast_gnp_random_graph(nodes, p=gnp_random_p))
    if graphModes == "all" or graphModes == "pref_att":
        graphs["pref_att"] = []
        for test in range(numtests):
            graphs["pref_att"].append(nx.barabasi_albert_graph(nodes, m=barabasi_m))
    if graphModes == "known":
        try:
            f=open("known.pickle")
        except IOError:
            print("File not found")
        else:
            graphs = pk.load(f)
            f.close()
    
    strategies = [
            "nodes_random",
            "nodes_deg",
            "nodes_bet",
            "degdist"
            ]
#    if nodeStrategy == "all":
#        for s in ["random", "deg", "bet", "close", "cluster"]:
#            strategies.append("nodes_"+s)
#    elif nodeStrategy != "none":
#        strategies.append("nodes_"+nodeStrategy)
  
#    if linkStrategy == "all":
#        for s in ["random", "bet"]:
#            strategies.append("links_"+s)
#    elif linkStrategy != "none":
#        strategies.append("links_"+linkStrategy)
  
    if verbose >= 3:
        print "Graph modes"
        print graphs.keys()
        print "Random graphs (nodes, links): "
        print [(len(G.nodes()),len(G.edges())) for G in graphs["random"]]
        print "Preferential attachment graphs (nodes, links): "
        print [(len(G.nodes()),len(G.edges())) for G in graphs["pref_att"]]
        print "Strategies: "
        print strategies
  
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
                plot.x.append(val[mode]["x"])
                plot.y.append((val[mode]["y"], mode))
        if s == "degdist":
            plot.title = "Degree distribution"
            plot.xAxisLabel = "Degree"
            plot.yAxisLabel = "Frequency"
            plot.legendPosition = "center right"
            plot.outFile = resultDir+"/degree_distribution"
            plot.plotData(style="o")
        else:
            plot.title = "Robustness metrics with "+s
            plot.xAxisLabel = "Fraction of failed links/nodes"
            plot.yAxisLabel = "Main cluster size / initial size"
            plot.legendPosition = "lower left"
            plot.outFile = resultDir+"/"+s+"_robustness"
            plot.plotData()