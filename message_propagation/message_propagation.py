import networkx as nx
import numpy as np
from collections import deque
from multiprocessing import Pool, cpu_count
import argparse, re
import random

class MessagePropagation:
    def __init__(self, graph, jobs, relays=[]):
        self.graph = graph
        self.jobs = jobs
        if relays == []:
            self.relays = graph.nodes()
        else:
            self.relays = relays

    def run(self, times=1000):
        T = [0 for u in self.graph]
        R = [0 for u in self.graph]
        for i in range(times):
            rk = map(self.propagate, self.graph.nodes())
            RK = set()
            for s in rk:
                RK = RK.union(s)
            for u in self.graph:
                t = set([(u,v) for v in self.graph if v != u])
                r = set([(v,u) for v in self.graph if v != u])
                if t <= RK:
                    T[u]+=1
                if r <= RK:
                    R[u]+=1
        T = [float(u)/times for u in T]
        R = [float(u)/times for u in R]
        return T, R

    def propagate(self, u):
        message = {}
        message['sender'] = u
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
                    v not in received_message):
                received_message.add(v)
                for i in message['content']:
                    route_knowledge.add((i,v))
                for w in self.graph[v].keys():
                    if w != u:
                        q.append((v,w))
        return route_knowledge

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testcase", help="path to the pickle file with the graph")
    parser.add_argument("-j", "--jobs",
            type=int,
            help="number of workers in the multiprocessing pool",
            default=cpu_count())
    args = parser.parse_args()

    G = nx.read_gpickle(args.testcase+"/graph.pickle")
    mp = MessagePropagation(G, args.jobs)
    #testname = re.search(r"(?P<file>[^/]*)$", args.testcase).group("name")
    resFile = open(args.testcase+"/results", "w+")
    resFile.write(str(mp.run()))
    resFile.close()
