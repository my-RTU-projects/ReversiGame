class Graph:
    def __init__(self):
        self.graph = list()

    def insert_node(self, parent_node_index, new_node_index):
        while len(self.graph) <= parent_node_index:
            self.graph.append(set())
        self.graph[parent_node_index].add(new_node_index)

    def remove_node(self, node_index):
        for refs in self.graph:
            if node_index in refs:
                refs.remove(node_index)
        if node_index < len(self.graph):
            self.graph[node_index].clear()

    def get_related_nodes(self, node_index):
        if node_index < len(self.graph):
            return self.graph[node_index]
        else:
            return set()

    def node_count(self):
        return len(self.graph)
