def topological_sort(graph, recursion_limit=250):
    visited = set()
    result = []

    def dfs(node, depth):
        if recursion_limit is not None and depth > recursion_limit:
            return
            raise RecursionError("Recursion limit exceeded")
        
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, depth + 1)
        result.append(node)

    for node in graph:
        if node not in visited:
            dfs(node, 1)

    return result[::-1]

# Example usage:
# Define a graph as a dictionary of nodes and their edges
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}

def are_all_items_in_set_using_issubset(items, my_set):
    # print(f"items: {items}")
    # print(f"my_set: {my_set}")
    return set(items).issubset(my_set)

def topological_sort_until_all_packages(graph1, graph2):

    sorted_nodes = topological_sort(graph1)

    packages = set()
    reduced_packages_list = []
    for node in sorted_nodes:
        flag = False
        if node in list(graph2.keys()) and node not in packages:
            flag = True
            # print(f"adding {node}")
            packages.add(node)
        for package in graph1[node]:
            if package in list(graph2.keys()) and package not in packages:
                flag = True
                # print(f"adding {package} from {node}")
                packages.add(package)
        if flag:        
            reduced_packages_list.append(node)
            if are_all_items_in_set_using_issubset(list(graph2.keys()), packages):
                break
        # print(len(reduced_packages_list), len(set(list(graph2.keys())) & packages))
    return reduced_packages_list
