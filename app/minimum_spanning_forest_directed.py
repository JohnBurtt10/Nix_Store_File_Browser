import networkx as nx
import matplotlib.pyplot as plt

def visualize_directed_graph(edges):
    G = nx.DiGraph()
    G.add_edges_from(edges)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=700, node_color='skyblue', font_size=8, arrowsize=20, arrowstyle='->')
    plt.title("Minimum Spanning Forest Visualization")
    plt.show()

def find_nodes_with_no_outgoing_arrows(graph, result_directed):
    all_nodes = set(graph.keys())
    nodes_with_arrows = set(v for u, v in result_directed)
    nodes_without_arrows = all_nodes - nodes_with_arrows
    return list(nodes_without_arrows)

class UnionFind:
    def __init__(self, elements):
        self.parent = {element: element for element in elements}
        self.rank = {element: 0 for element in elements}

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)

        if root_u != root_v:
            if self.rank[root_u] < self.rank[root_v]:
                self.parent[root_u] = root_v
            elif self.rank[root_u] > self.rank[root_v]:
                self.parent[root_v] = root_u
            else:
                self.parent[root_v] = root_u
                self.rank[root_u] += 1

#TODO: partioned references
def minimum_spanning_forest_directed(graph):
    edges = []

    # Extract edges from the directed graph
    try:
        for u in graph:
            #TODO: ??
            for partition in graph[u]:
                for v in partition:
                    edges.append((u, v))
    except Exception as e:
        print(f"{graph[u]}")

    # Sort edges by the weight, considering only forward edges (u -> v)
    edges.sort(key=lambda x: x[1])

    vertices = set(node for edge in edges for node in edge)
    uf = UnionFind(vertices)

    msf = []

    for edge in edges:
        u, v = edge

        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            msf.append((u, v))

    return msf


def main():
    # Example usage with a directed graph using string identifiers
    graph_directed = {
        'A': ['B', 'F', 'G', 'K'],
        'B': ['C', 'D'],
        'C': ['A'],
        'D': ['E'],
        'E': [],
        'I': []
    }

    # Iterate over the dictionary
    # for key, value_list in graph_directed.items():
    #     # Filter the list to keep only items that are keys in the dictionary
    #     graph_directed[key] = [item for item in value_list if item in graph_directed]

    result_directed = minimum_spanning_forest_directed(graph_directed)

    visualize_directed_graph(result_directed)

    # Find nodes without outgoing arrows
    nodes_without_arrows = find_nodes_with_no_outgoing_arrows(
        graph_directed, result_directed)
    
    # overlap = [value for value in nodes_without_arrows if value in list(graph_directed.keys())]

    print("Nodes without outgoing arrows:", nodes_without_arrows)

    # print(f"overlap: {overlap}")


if __name__ == "__main__":
    main()
