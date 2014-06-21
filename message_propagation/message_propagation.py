import networkx as nx
from collections import deque
from multiprocessing import cpu_count
import mpr
import random
import os
import argparse
import time
from collections import defaultdict
import re


class MessagePropagation:
    def __init__(self, graph, mode, jobs):
        self.graph = graph
        self.jobs = jobs
        self.mode = mode

    def run(self, times=1000):
        # T = [0 for u in self.graph]
        # R = [0 for u in self.graph]
        # routes_from = [set([(u, v) for v in self.graph if v != u])
        #                for u in self.graph]
        # routes_to = [set([(v, u) for v in self.graph if v != u])
        #              for u in self.graph]
        T = defaultdict(float)
        R = defaultdict(float)
        routes_to = defaultdict(set)
        routes_from = defaultdict(set)
        for u in self.graph:
            T[u] = 0
            R[u] = 0
            for v in self.graph:
                if v != u:
                    routes_from[u].add((u, v))
                    routes_to[u].add((v, u))
        if self.mode == "mpr":
            self.mprSolution = mpr.solveMPRProblem(self.graph)
            originatorSet = set()
            for s in self.mprSolution.values():
                originatorSet.update(list(s)[0])
            originators = list(originatorSet)
        else:
            originators = self.graph.nodes()
        for i in range(times):
            # each node initially only knows itself
            known_routes = set([(u, u) for u in self.graph])
            for u in originators:
                rk = self.propagate(u)
                known_routes = known_routes.union(rk)
            for u in self.graph:
                if routes_from[u] <= known_routes:
                    T[u] += 1
                if routes_to[u] <= known_routes:
                    R[u] += 1
        T = [float(u) / times for u in T.values()]
        R = [float(u) / times for u in R.values()]
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
            q.append((u, v))
        while len(q) > 0:
            u, v = q.popleft()
            if (self.process_message(u, v, received_message)):
                received_message.add(v)
                for i in message['content']:
                    route_knowledge.add((i, v))
                if (self.forward_message(u, v)):
                    for w in self.graph[v].keys():
                        if w != u:
                            q.append((v, w))
        return route_knowledge

    def process_message(self, u, v, received_message):
        n = random.random()
        if n <= self.graph[u][v]['weight']:
            # The link failed
            return False
        if v in received_message:
            # The message was already processed by v
            return False
        return True

    def forward_message(self, u, v):
        if (self.mode == "mpr"):
                #and v not in list(self.mprSolution[u])[0]):
            isMPR = False
            for solution in self.mprSolution[u]:
                if v in solution:
                    isMPR = True
            if not isMPR:
                # v is not selected as an MPR of u
                return False
        return True


class ResultFile:
    def __init__(self, directory, basename):
        self.basename = basename
        l = []
        for f in os.listdir(directory):
            match = re.match("{}-(?P<num>\d+)".format(basename), f)
            if match:
                l.append(match.group('num'))
        if len(l) > 0:
            new = int(sorted(l)[-1]) + 1
        else:
            new = 0
        self.path = "{dir}/{name}-{num}".format(dir=directory,
                                                name=basename,
                                                num=new)
        self.fo = open(self.path, "w+")


def strip_trailing_slash(string):
    if string.endswith('/'):
        string = string[:-1]
    return string


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "testcase",
        type=strip_trailing_slash,
        help="path to the pickle file with the graph")
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        help="number of workers in the multiprocessing pool",
        default=cpu_count())
    parser.add_argument(
        "-m", "--mode",
        choices=["default", "batman", "mpr"],
        help="propagation mode, see description",
        default="default")
    args = parser.parse_args()

    G = nx.read_gpickle(args.testcase + "/graph.pickle")
    mp = MessagePropagation(G, args.mode, args.jobs)
    #testname = re.search(r"(?P<file>[^/]*)$", args.testcase).group("name")
    res = mp.run()
    date = time.strftime("%Y%m%d-%H%M")
    resFile = ResultFile(args.testcase, "T-{m}".format(m=args.mode)).fo
    for u in res[0]:
        resFile.write("%f\n" % u)
    resFile.close()
    resFile = ResultFile(args.testcase, "R-{m}".format(m=args.mode)).fo
    for u in res[1]:
        resFile.write("%f\n" % u)
    resFile.close()
