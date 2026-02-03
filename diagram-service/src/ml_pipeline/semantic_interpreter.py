import networkx as nx
from typing import Dict, Any, List

from src.core.logger import app_logger
from src.utils.graph_utils import get_node_successors, get_node_predecessors, calculate_node_levels


class SemanticInterpreter:
    def __init__(self):
        app_logger.info("SemanticInterpreter initialized")
        
        self.shape_keywords = {
            'start': ['начало', 'start', 'старт', 'begin'],
            'end': ['конец', 'end', 'финиш', 'finish', 'stop'],
            'decision': ['если', 'if', 'условие', 'condition', 'выбор', 'choice', '?'],
            'process': ['обработка', 'process', 'действие', 'action', 'выполнить', 'execute'],
            'data': ['данные', 'data', 'ввод', 'input', 'вывод', 'output']
        }
    
    def interpret(self, graph: nx.DiGraph) -> Dict[str, Any]:
        try:
            app_logger.debug(f"Interpreting graph with {graph.number_of_nodes()} nodes")
            
            self._classify_node_types(graph)
            
            self._analyze_flow(graph)
            
            self._extract_logic(graph)
            
            interpretation = {
                'nodes': self._extract_nodes_info(graph),
                'edges': self._extract_edges_info(graph),
                'flow_type': self._determine_flow_type(graph),
                'complexity': self._calculate_complexity(graph)
            }
            
            app_logger.info("Graph interpretation complete")
            return interpretation
            
        except Exception as e:
            app_logger.error(f"Semantic interpretation failed: {str(e)}", exc_info=True)
            return {'nodes': [], 'edges': [], 'flow_type': 'unknown', 'complexity': 0}
    
    def _classify_node_types(self, graph: nx.DiGraph):
        for node in graph.nodes():
            label = graph.nodes[node].get('label', '').lower()
            current_type = graph.nodes[node].get('type', 'process')
            
            for node_type, keywords in self.shape_keywords.items():
                if any(keyword in label for keyword in keywords):
                    graph.nodes[node]['type'] = node_type
                    app_logger.debug(f"Classified {node} as {node_type} based on label")
                    break
            
            successors = get_node_successors(graph, node)
            if len(successors) > 1 and current_type != 'decision':
                graph.nodes[node]['type'] = 'decision'
                app_logger.debug(f"Classified {node} as decision based on branching")
    
    def _analyze_flow(self, graph: nx.DiGraph):
        levels = calculate_node_levels(graph)
        
        for node in graph.nodes():
            graph.nodes[node]['level'] = levels.get(node, 0)
        
        for node in graph.nodes():
            successors = get_node_successors(graph, node)
            predecessors = get_node_predecessors(graph, node)
            
            graph.nodes[node]['out_degree'] = len(successors)
            graph.nodes[node]['in_degree'] = len(predecessors)
    
    def _extract_logic(self, graph: nx.DiGraph):
        for node in graph.nodes():
            node_type = graph.nodes[node].get('type', 'process')
            
            if node_type == 'decision':
                successors = get_node_successors(graph, node)
                if len(successors) == 2:
                    graph.edges[node, successors[0]]['condition'] = 'true'
                    graph.edges[node, successors[1]]['condition'] = 'false'
    
    def _extract_nodes_info(self, graph: nx.DiGraph) -> List[Dict[str, Any]]:
        nodes_info = []
        for node in graph.nodes():
            node_data = dict(graph.nodes[node])
            node_data['id'] = node
            nodes_info.append(node_data)
        return nodes_info
    
    def _extract_edges_info(self, graph: nx.DiGraph) -> List[Dict[str, Any]]:
        edges_info = []
        for source, target in graph.edges():
            edge_data = dict(graph.edges[source, target])
            edge_data['source'] = source
            edge_data['target'] = target
            edges_info.append(edge_data)
        return edges_info
    
    def _determine_flow_type(self, graph: nx.DiGraph) -> str:
        has_cycles = False
        try:
            cycles = list(nx.simple_cycles(graph))
            has_cycles = len(cycles) > 0
        except:
            pass
        
        has_branches = any(
            len(get_node_successors(graph, node)) > 1
            for node in graph.nodes()
        )
        
        if has_cycles:
            return 'cyclic'
        elif has_branches:
            return 'branching'
        else:
            return 'sequential'
    
    def _calculate_complexity(self, graph: nx.DiGraph) -> int:
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()
        num_decisions = sum(
            1 for node in graph.nodes()
            if graph.nodes[node].get('type') == 'decision'
        )
        
        complexity = num_nodes + num_edges + (num_decisions * 2)
        return complexity
    
    def generate_description(self, graph: nx.DiGraph) -> str:
        try:
            interpretation = self.interpret(graph)
            
            description_parts = []
            
            flow_type = interpretation['flow_type']
            if flow_type == 'sequential':
                description_parts.append("Алгоритм выполняется последовательно.")
            elif flow_type == 'branching':
                description_parts.append("Алгоритм содержит ветвления и условия.")
            elif flow_type == 'cyclic':
                description_parts.append("Алгоритм содержит циклы.")
            
            nodes = interpretation['nodes']
            sorted_nodes = sorted(nodes, key=lambda n: n.get('level', 0))
            
            for node in sorted_nodes:
                node_type = node.get('type', 'process')
                label = node.get('label', '')
                
                if node_type == 'start':
                    description_parts.append(f"Начало: {label}")
                elif node_type == 'end':
                    description_parts.append(f"Конец: {label}")
                elif node_type == 'decision':
                    description_parts.append(f"Проверка условия: {label}")
                elif node_type == 'process':
                    description_parts.append(f"Выполнение: {label}")
            
            return ' '.join(description_parts)
            
        except Exception as e:
            app_logger.error(f"Failed to generate description: {str(e)}")
            return "Не удалось сгенерировать описание алгоритма."
