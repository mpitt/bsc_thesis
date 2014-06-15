---
title: Advanced Topology Analysis in Three Wireless Community Networks
author: Michele Pittoni
date: 2014 - VI
bibliography: thesis.bib
...

\chapterstyle{section}

# Introduction
Wireless Community Networks, a particular kind of wireless mesh networks, have become more and more popular in recent years. Their peculiar nature of self-organizing networks requires a tailored analysis, given the complexity of topologies that can arise. Much research effort is being dedicated to the development of new routing protocols for this networks and for measuring their efficiency.

This works provides an introduction to the topic of Wireless Community Networks and a description of the three networks which are subsequently analysed. Also provided is an introduction to OLSR, the routing protocol which is used in the analysed networks. The biggest part focuses on the analysis of some efficiency metrics for the chosen networks and a comparison with some well known random network models.

# Wireless Community Networks
Wireless Community Networks (WCNs) have existed since 2000 and have gained popularity with the decrease of the cost for Wi-Fi equipment. The idea behind them is simple but powerful: leveraging Wi-Fi technology to create a network which is owned by citizens instead of corporations. The basic component of a WCN is the node, which usually consists of a router with some wireless interfaces attached. Most nodes have one or more directional interfaces to communicate with other nodes and some also have an omnidirectional interface to serve as an Access Point (AP).

Because of their nature of not asking permissions, it is difficult to determine precisely the number of active WCNs as there is no central registry to look at. However, there is a Wikipedia page^[@_list_2014] which, albeit incomplete, lists 262 WCNs at the time of writing. The dimensions of such networks are varied, from just a handful of nodes to nearly 25,000 as in Guifi^[http://guifi.net], which is probably the world's largest WCN.

The three WCNs which are analysed later are Ninux, Funkeuer Wien and Funkfeuer Graz.

### Ninux
Ninux is the largest italian WCN. It was started in 2001 in Rome and now consists of about 250 active nodes, located in different "Ninux islands" all over Italy.

OLSR is used as the routing protocol inside islands.

### FFWien

### FFGraz

# OLSR summary

# Robustness analysis
The first metric analysed is the robustness of the network. The chosen methodology is a variation of the percolation problem described in Chapter 16 of [@newman_networks:_2010].<!--_-->

Defining robustness is not trivial. While it is intuitive that removing nodes or links affects the network ability to successfully transport information, it is not obvious how this ability can be quantified. Moreover, nodes and links in a network are note all equal, neither in the impact of their removal nor in their probability of failure in the real world.

The first concern is traditionally addressed in literature by considering the connected components of the remaining graph. Specifically, the metric is defined as the ratio

\begin{equation}
S = \frac{\text{size of the largest connected component}}
{\text{size of the original graph}}
\end{equation}

Then the inequalities of nodes and link must be taken into account. This is a more complicated matter because there is not a single correct solution. The approach largely depends on the real world situation to be analysed. For example, to evaluate the robustness of a network to random equipment failures the nodes can be removed in a random order. On the other hand, to simulate a targeted attack scenario the nodes with highest degree can be removed first, assuming attackers will direct their action to cause the highest possible damage. Other node or link metrics can be used in the same way, to simulate other scenarios.

Here different criteria have been used to gather a broad set of data. Specifically, nodes were first removed randomly with uniform probability, as in the classic percolation problem. Then they were removed following the order based on the following criterias.

Degree
  : The degree of a node is the number of edges connected to that node
Betweenness centrality
  : The beetweennes centrality of a node is the fraction of the shortest paths between any two other nodes that pass through that node
Closeness centrality
  : The closeness centrality of a node is the mean lenght of the shortest paths from that node to every other node
Clustering coefficient
  : TODO explanation

## Analysed networks
In addition to the three WCNs, some graph have been generated based on known random graph models.

* Erd\H{o}s-Renyi random network (`fast_gnp_random_graph`)
* Scale free network with a power law distribution (`barabasi_albert_graph`)

# Message propagation analysis

### The importance of routing
The robustness of a network is based on a static analysis of the connectivity of the network graph when removing nodes or links. A communication network, however, is a dynamic system where information needs to move between nodes. Moreover, the decentralised nature of computer networks means that the complete topology of the network is not necessarily the topology used to transmit information, depending on the routing protocol used for the network.

Given this, in order to understand the behaviour of a communication network we need to study the behaviour of its routing protocol with different underlying topologies. We are interested in the phase of topology discovery, where each node receives information on the existence of the other nodes in the network and (part of) the route to reach them.

Topology discovery in link state routing protocols is usually performed with each node flooding the network with some kind of `hello` message. The possible variations are the flooding policy and the contents of the message. The most popular routing protocols used in mesh networks behave as follows:

* B.A.T.M.A.N. uses the simplest possible flooding (each node just performs a duplicate detection to avoid loops) and the `hello` message contains the sender address and a sequence number (for the duplicate detection)
* OLSR employs a more sophisticated flooding mechanism based on MPRs and the `hello` message contains the whole neighbourhood of the sender
* versions of OLSR used in practice usually force each node to be an MPR ^[@maccari_analysis_2013], thus having an hybrid behaviour with flooding as in B.A.T.M.A.N.

### Problem definition
The network is represented by a weighted graph $G=(N,E)$, where weights represent the probability of losing a packet on each link (we use the ETX metric of OLSR for this purpose).

Each node creates a message with information on its neighbourhood and propagates it to each neighbour. Each node also propagates the message it receives, with a simple duplicate detection based on the sender to avoid loops.

Further iterations of the analysis will consider a subset of nodes generating and propagating the messages and a different protocol for loop avoidance.

Given the above situation, we define

> $T_u = \forall v \in N .$ ``node $v$ has a route to node $u$''

> $R_u = \forall v \in N .$ ``node $u$ has a route to node $v$''

Determine the probability of $T_u$ and $R_u$ for each node $u$ in the graph.

### Methodology
The propagation of a message with duplicate detection can be simulated with a Breadth First Search (BFS) over the graph. The most important variation is that before traversing an edge a random number is generated and compared to the packet loss probability of that link, to check if the transmission succeeds.
During the BFS, the simulation keeps track of which nodes received the message and based on the content of the message determines the couples of nodes which have a known route between themselves.
The search is repeated for every node as the starting point. The union of the results is then used to verify $T_u$ and $R_u$.

The random simulation is run 1000 times to gather a significant figure of the probability of $T_u$ and $R_u$.

The propagation for a node is as follows in pseudocode:

#####function propagate(Graph g, Node u)
```
message_sender <- u
message_content <- neighbourhood_of(u)
q <- Queue()
route_knowledge <- set()
u.visited <- True
for v in u.neighbours append (u,v) to q
while q is not empty do
    pop (u,v) from q
    n <- random()
    if (not v.visited) and (n ≥ weight(u,v))
        v.visited <- True
        for i in message_content
            add (i,v) to route_knowledge
        for w in v.neighbours append (v,w) to q if w ≠ u
return route_knowledge
```

The function is run for each node in the graph an the results are collected.

#####function propagate_all(Graph g)
```
rk <- set()
t, r <- array()
for u in g
    rk <- rk ∪ propagate(g, u)
for u in g
    if (u,v) ∈ rk ∀ node v ≠ u
        t[u] <- 1
    else
        t[u] <- 0
    if (v,u) ∈ rk ∀ node v ≠ u
        r[u] <- 1
    else
        r[u] <- 0
return t, r
```

#####function run_simulation(Graph g, Integer n)
```
pt, pr <- array()
for n times
    t, r <- propagate_all(g)
    pt += t                                % sum each element
    pr += r                                % "
divide each element of pt by n
divide each element of pr by n
return pt, pr
```

### Rationale
The feasibility of calculating $T_u$ and $R_u$ exactly has been evaluated. However, the computational complexity of this approach seems very high and likely does not justify its use in place of the Monte Carlo simulation.

Going into the details, the probability of a message propagating from node $u$ to node $v$ is easily calculated by... ~~summing the probabilities of success for every simple path between the two nodes.~~ With this result for every possible destination $v1\ldots vn$ of a message transmitted by $u$, it's theoretically possible to calculate $T_u$ but it's not easy: the events "reaching v1"..."reaching vn" are not independent, so the probability of "reaching every node" is not the product of their probabilities.

For example, if $w$ is in any simple path from $u$ to $v$, the probability of success between $u$ and $v$ changes if it is known that node $w$ has been reached.

$P(v) = P(w) \cdot P(v|w) + P(\lnot w) \cdot P(v|\lnot w)$

The value of $P(v|w)$ and $P(v|\lnot w)$ is not so obvious:

* $P(v|w)$ is the sum of the probabilities of the subpaths $w \rightarrow v$ for every simple path $u→v$
* $P(v|\lnot w)$ is the sum of the probabilities of success for simple paths from $u$ to $v$ excluding the paths that contain $w$

This must be computed for every $w$ that appears in at least one simple path $u \rightarrow v$. Again, this computation must be repeated for every possible source-destination pair $u,v$.

### Developments
Save the paths in order to figure out which one is the best (between the ones that succeeded in the simulation)

* No neighbours (B.A.T.M.A.N.)
* MPR (see ninux-topology-analyzer for MPR solver)

# Conclusions

# Bibliography
