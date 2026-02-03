import networkx as nx
from typing import List, Dict, Any, Tuple, Optional

from src.core.logger import app_logger
from src.core.exceptions import GraphConstructionError


def create_directed_graph() -> nx.DiGraph:
    return nx.DiGraph()


def add_node(graph: nx.DiGraph, node_id: str, **attributes) -> None:
    graph.add_node(node_id, **attributes)


def add_edge(graph: nx.DiGraph, source: str, target: str, **attributes) -> None:
    graph.add_edge(source, target, **attributes)


def validate_graph(graph: nx.DiGraph) -> Tuple[bool, List[str]]:
    errors = []
    
    if graph.number_of_nodes() == 0:
        errors.append("Graph has no nodes")
    
    if not nx.is_weakly_connected(graph):
        errors.append("Graph is not connected")
    
    start_nodes = [n for n in graph.nodes() if graph.nodes[n].get('type') == 'start']
    if len(start_nodes) == 0:
        errors.append("Graph has no start node")
    elif len(start_nodes) > 1:
        errors.append(f"Graph has multiple start nodes: {start_nodes}")
    
    end_nodes = [n for n in graph.nodes() if graph.nodes[n].get('type') == 'end']
    if len(end_nodes) == 0:
        errors.append("Graph has no end node")
    
    for node in graph.nodes():
        if 'type' not in graph.nodes[node]:
            errors.append(f"Node {node} has no type attribute")
    
    return len(errors) == 0, errors


def find_cycles(graph: nx.DiGraph) -> List[List[str]]:
    try:
        cycles = list(nx.simple_cycles(graph))
        return cycles
    except Exception as e:
        app_logger.warning(f"Failed to find cycles: {str(e)}")
        return []


def topological_sort(graph: nx.DiGraph) -> Optional[List[str]]:
    try:
        if nx.is_directed_acyclic_graph(graph):
            return list(nx.topological_sort(graph))
        else:
            app_logger.warning("Graph contains cycles, cannot perform topological sort")
            return None
    except Exception as e:
        app_logger.error(f"Failed to perform topological sort: {str(e)}")
        return None


def get_node_successors(graph: nx.DiGraph, node_id: str) -> List[str]:
    return list(graph.successors(node_id))


def get_node_predecessors(graph: nx.DiGraph, node_id: str) -> List[str]:
    return list(graph.predecessors(node_id))


def graph_to_dict(graph: nx.DiGraph) -> Dict[str, Any]:
    nodes = []
    for node_id in graph.nodes():
        node_data = {"id": node_id}
        node_data.update(graph.nodes[node_id])
        nodes.append(node_data)
    
    edges = []
    for source, target in graph.edges():
        edge_data = {"source": source, "target": target}
        edge_data.update(graph.edges[source, target])
        edges.append(edge_data)
    
    return {"nodes": nodes, "edges": edges}


def dict_to_graph(data: Dict[str, Any]) -> nx.DiGraph:
    graph = nx.DiGraph()
    
    for node in data.get("nodes", []):
        node_id = node.pop("id")
        graph.add_node(node_id, **node)
    
    for edge in data.get("edges", []):
        source = edge.pop("source")
        target = edge.pop("target")
        graph.add_edge(source, target, **edge)
    
    return graph


def calculate_node_levels(graph: nx.DiGraph) -> Dict[str, int]:
    levels = {}
    
    start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
    
    if not start_nodes:
        start_nodes = list(graph.nodes())[:1]
    
    for start in start_nodes:
        levels[start] = 0
    
    visited = set(start_nodes)
    queue = list(start_nodes)
    
    while queue:
        current = queue.pop(0)
        current_level = levels[current]
        
        for successor in graph.successors(current):
            if successor not in visited:
                levels[successor] = current_level + 1
                visited.add(successor)
                queue.append(successor)
            else:
                levels[successor] = max(levels[successor], current_level + 1)
    
    return levels


def get_graph_statistics(graph: nx.DiGraph) -> Dict[str, Any]:
    return {
        "num_nodes": graph.number_of_nodes(),
        "num_edges": graph.number_of_edges(),
        "is_dag": nx.is_directed_acyclic_graph(graph),
        "is_connected": nx.is_weakly_connected(graph),
        "num_cycles": len(find_cycles(graph)),
        "density": nx.density(graph)
    }


def merge_graphs(graph1: nx.DiGraph, graph2: nx.DiGraph) -> nx.DiGraph:
    merged = nx.DiGraph()
    merged.add_nodes_from(graph1.nodes(data=True))
    merged.add_nodes_from(graph2.nodes(data=True))
    merged.add_edges_from(graph1.edges(data=True))
    merged.add_edges_from(graph2.edges(data=True))
    return merged
