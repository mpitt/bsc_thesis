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
        T = R = [0 for u in self.graph]
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
        T = [t/float(times) for t in T]
        R = [r/float(times) for r in R]
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

    # This is probably an hack:
    # Pool.map needs to pickle MessagePropagation.propagate
    # see http://bytes.com/topic/python/answers/552476-why-cant-you-pickle-instancemethods
    def _pickle_method(method):
        func_name = method.im_func.__name__
        obj = method.im_self
        cls = method.im_class
        return _unpickle_method, (func_name, obj, cls)

    def _unpickle_method(func_name, obj, cls):
        for cls in cls.mro():
            try:
                func = cls.__dict__[func_name]
            except KeyError:
                pass
            else:
                break
            return func.__get__(obj, cls)

    import copy_reg
    import types
    copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
    # /hack

    G = nx.read_gpickle(args.testcase)
    mp = MessagePropagation(G, args.jobs)
    testname = re.search(r"(?P<name>[^/]*)\.pickle$", args.testcase).group("name")
    print mp.run()
