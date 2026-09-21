import heapq

def build_graph(roads):
    graph = {}
    for road in roads:
        if road["status"].upper() != "OPEN":
            continue
        a = road["from_location"]
        b = road["to_location"]
        d = float(road["distance"])
        graph.setdefault(a, []).append((b, d))
        graph.setdefault(b, []).append((a, d))
    return graph

def shortest_path(graph, start, end):
    queue = [(0.0, start, [])]
    visited = set()

    while queue:
        cost, node, path = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if node == end:
            return cost, path

        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return None, []
