## Message propagation analysis

### Scope
Given a weighted graph `G=(N,E)`, where weights represent the probability of losing a packet on each link, calculate the probability that route information about a node successfully propagates to the entire graph.

Each node creates a message with information on its neighbourhood and propagates it to each neighbour. Each node also propagates the message it receives, with a simple duplicate detection based on the sender to avoid loops.

Further iterations of the analysis will consider a subset of nodes generating and propagating the messages and a different protocol for loop avoidance.

### Problem definition
Given the above situation, we define

```
T_u = "∀ v ∈ N . node v has a route to node u"
```
```
R_u = "∀ v ∈ N . node u has a route to node v"
```

Determine the probability of `T_u` and `R_u` for each node `u` in the graph.

### Methodology
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

### Rationale
The feasibility of an analytical approach to calculate `T_u` and `R_u` exactly has been evaluated. However, the computational complexity of this approach seems very high and likely does not justify its use in place of the Monte Carlo simulation.

Going into the details, the probability of a message propagating from node `u` to node `v` is easily calculated by summing the probabilities of success for every simple path between the two nodes. With this result for every possible destination `v1...vn` of a message transmitted by `u`, it's theoretically possible to calculate `T_u` but it's not easy: the events "reaching v1"..."reaching vn" are not independent, so the probability of "reaching every node" is not the product of their probabilities.

For example, if `w` is in any simple path from `u` to `v`, the probability of success between `u` and `v` changes if it is known that node `w` has been reached.

`P(v) = P(w)*P(v|w) + (1-P(w))*P(v|¬w)`

The value of `P(v|w)` and `P(v|¬w)` is not so obvious:

* `P(v|w)` is the sum of the probabilities of the subpaths `w→v` for every simple path `u→v`
* `P(v|¬w)` is the sum of the probabilities of success for simple paths from `u` to `v` excluding the paths that contain `w`

This must be computed for every `w` that appears in at least one simple path `u→v`. Again, this computation must be repeated for every possible source-destination pair `u,v`.