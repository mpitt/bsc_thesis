## Message propagation analysis

#### Scope
Given a weighted graph `G=(N,E)`, where weights represent the probability of losing a packet on each link, calculate the probability that route information about a node successfully propagates to the entire graph.

Each node creates a message with information on its neighbourhood and propagates it to each neighbour. Each node also propagates the message it receives, with a simple duplicate detection based on the sender to avoid loops.

Further iterations of the analysis will consider a subset of nodes generating and propagating the messages and a different protocol for loop avoidance.

#### Problem definition
Given the above situation, we define

```
T_u = "∀ v ∈ N . node v has a route to node u"
```
```
R_u = "∀ v ∈ N . node u has a route to node v"
```

Determine the probability of `T_u` and `R_u` for each node `u` in the graph.

#### Methodology
The propagation of a message with duplicate detection can be simulated with a Breadth First Search (BFS) over the graph. The most important variation is that before traversing an edge a random number is generated and compared to the packet loss probability of that link, to check if the transmission succeeds.
During the BFS, the simulation keeps track of which nodes received the message and based on the content of the message determines the couples of nodes which have a known route between themselves.
The search is repeated for every node as the starting point. The union of the results is then used to verify `T_u` and `R_u`.

The random simulation is run 1000 times to gather a significant figure of the probability of `T_u` and `R_u`.

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