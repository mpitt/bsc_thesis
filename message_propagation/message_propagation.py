import networkx as nx
import numpy as np
from collections import deque
from multiprocessing import Pool, cpu_count
import argparse, re, random, time, os
import mpr

class MessagePropagation:
    def __init__(self, graph, mode, jobs):
        self.graph = graph
        self.jobs = jobs
        self.mode = mode

    def run(self, times=1000):
        T = [0 for u in self.graph]
        R = [0 for u in self.graph]
        routes_from = [set([(u,v) for v in self.graph if v != u]) for u in self.graph]
        routes_to = [set([(v,u) for v in self.graph if v != u]) for u in self.graph]
        if self.mode == "mpr":
            self.mprSolution = mpr.solveMPRProblem(self.graph)
            originatorSet = set()
            for s in self.mprSolution.values():
                originatorSet.update(list(s)[0])
            originators = list(originatorSet)
        else:
            originators = self.graph.nodes()
        for i in range(times):
            known_routes = set()
            for u in originators:
                rk = self.propagate(u)
                known_routes = known_routes.union(rk)
            for u in self.graph:
                if routes_from[u] <= known_routes:
                    T[u]+=1
                if routes_to[u] <= known_routes:
                    R[u]+=1
        T = [float(u)/times for u in T]
        R = [float(u)/times for u in R]
        return T, R

    def propagate(self, u):
        message = {}
        message['sender'] = u
        if self.mode == "batman":
            message['content'] = [u]
        else:
            message['content'] = [u] + self.graph.neighbors(u)
        q = deque()
        route_knowledge = set()
        received_message = set([u])
        for v in self.graph[u].keys():
            q.append((u,v))
        while len(q) > 0:
            u,v = q.popleft()
            n = random.random()
            if (n >= self.graph[u][v]['weight'] and
                    v not in received_message
                    and (
                        self.mode != "mpr" or
                        v in list(self.mprSolution[u])[0]
                        )
                    ):
                received_message.add(v)
                for i in message['content']:
                    route_knowledge.add((i,v))
                for w in self.graph[v].keys():
                    if w != u:
                        q.append((v,w))
        return route_knowledge

class ResultFile:
    def __init__(self, directory, basename):
        self.basename = basename
        l = filter(lambda x: x.startswith(basename), os.listdir(directory))
        if len(l) > 0:
            last = sorted(l, key=self.filenumber)[-1]
            new = self.filenumber(last) + 1
        else:
            new = 0
        self.path = directory+"/"+basename+"-"+str(new)
        self.fo = open(self.path, "w+")

    def filenumber(self, filename):
        start = len(self.basename) + 1
        num = filename[start:]
        return int(num)

def strip_trailing_slash(string):
    if string.endswith('/'):
        string = string[:-1]
    return string

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testcase",
            type=strip_trailing_slash,
            help="path to the pickle file with the graph")
    parser.add_argument("-j", "--jobs",
            type=int,
            help="number of workers in the multiprocessing pool",
            default=cpu_count())
    parser.add_argument("-m", "--mode",
            choices=["default", "batman", "mpr"],
            help="propagation mode, see description",
            default="default")
    args = parser.parse_args()

    G = nx.read_gpickle(args.testcase+"/graph.pickle")
    mp = MessagePropagation(G, args.mode, args.jobs)
    #testname = re.search(r"(?P<file>[^/]*)$", args.testcase).group("name")
    res = mp.run()
    date = time.strftime("%Y%m%d-%H%M")
    resFile = ResultFile(args.testcase, "T").fo
    resFile.write("T\n")
    for u in res[0]:
        resFile.write("%f\n" % u)
    resFile.close()
    resFile = ResultFile(args.testcase, "R").fo
    resFile.write("R\n")
    for u in res[1]:
        resFile.write("%f\n" % u)
    resFile.write("\n")
    resFile.close()
