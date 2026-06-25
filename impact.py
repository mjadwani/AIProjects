from collections import defaultdict

relationships = [
    ("CMTSTAT", "affects", "Thread Reuse"),
    ("Thread Reuse", "affects", "Thread Creation Rate"),
    ("Thread Creation Rate", "affects", "CPU Consumption"),
]

def get_direct_impacts(node: str):
    results = []

    for source, relation, target in relationships:
        if source.upper() == node.upper():
            results.append({
                "relation": relation,
                "target": target
            })

    return results






def get_impact_chain(node: str):
    graph = defaultdict(list)

    for source, relation, target in relationships:
        graph[source].append((relation, target))
    chain = []

    current = node

    while current in graph:
        relation, next_node = graph[current][0]

        chain.append({
            "source": current,
            "relation": relation,
            "target": next_node
        })

        current = next_node

    return chain







def find_path(start, target):
    graph = defaultdict(list)

    for source, relation, target in relationships:
        graph[source].append((relation, target))
    visited = set()

    def dfs(node, path):
        if node == target:
            return path

        visited.add(node)

        for relation, next_node in graph.get(node, []):
            if next_node not in visited:

                result = dfs(
                    next_node,
                    path + [(node, relation, next_node)]
                )

                if result:
                    return result

        return None

    return dfs(start, [])



if __name__ == "__main__":
    print(get_direct_impacts('CMTSTAT'))
    print(get_impact_chain('CMTSTAT'))
    print(find_path("CMTSTAT","CPU Consumption"))