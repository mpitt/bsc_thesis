## Robustness analysis of synthetic topologies

#### Scope
Analysing the robustness of different kinds of graphs of known topology.

#### Methodology
For each kind of topology generate and analyse 30 different graphs, then compute an average of the results.

#### Topologies
* Random network (`fast_gnp_random_graph`)
* Scale free network with a power law distribution (`barabasi_albert_graph`)

#### Computing strategies
Different strategies have been used to test the robustness under different conditions. All the computations were done by removing nodes one at a time and computing the size of the giant cluster of the remaining graph. The order in which nodes were removed varied between strategies.

###### Random removal
The first strategy was to randomly select the order of the node removal, to simulate random independent failures of network components. This test was repeated 30 times per graph, with a different order each time.

###### Ordered removal
To simulate an attack on the most strategic nodes of the network, the nodes were removed ordered by different metrics, such as:

* degree
* betweenness centrality
* closeness centrality
* ratio of degree over clustering coefficient

The metrics were calculated on the original graph and used to order the nodes. The metrics and the order were not updated after the removal of each node, in order to avoid increasing the complexity too much. For these metrics, only one test was done on each graph (since the order would not have changed anyway).