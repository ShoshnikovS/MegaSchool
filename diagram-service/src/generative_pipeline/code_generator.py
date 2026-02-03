import networkx as nx
from typing import Literal

from src.core.logger import app_logger
from src.utils.graph_utils import get_node_successors


class DiagramCodeGenerator:
    def __init__(self):
        app_logger.info("DiagramCodeGenerator initialized")
    
    def generate(
        self,
        graph: nx.DiGraph,
        format: Literal['plantuml', 'mermaid'] = 'plantuml'
    ) -> str:
        try:
            app_logger.debug(f"Generating {format} code for graph with {graph.number_of_nodes()} nodes")
            
            if format == 'plantuml':
                code = self._generate_plantuml(graph)
            elif format == 'mermaid':
                code = self._generate_mermaid(graph)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            app_logger.info(f"Generated {format} code successfully")
            return code
            
        except Exception as e:
            app_logger.error(f"Code generation failed: {str(e)}", exc_info=True)
            return f"# Error generating {format} code: {str(e)}"
    
    def _generate_plantuml(self, graph: nx.DiGraph) -> str:
        lines = ["@startuml"]
        lines.append("skinparam defaultTextAlignment center")
        lines.append("skinparam backgroundColor white")
        lines.append("")
        
        node_mapping = {}
        for idx, node in enumerate(graph.nodes()):
            node_id = f"n{idx}"
            node_mapping[node] = node_id
            
            node_type = graph.nodes[node].get('type', 'process')
            label = graph.nodes[node].get('label', node)
            
            if node_type == 'start':
                lines.append(f"start")
                if label and label.lower() != 'начало' and label.lower() != 'start':
                    lines.append(f":{label};")
            elif node_type == 'end':
                lines.append(f"stop")
            elif node_type == 'decision':
                successors = get_node_successors(graph, node)
                if len(successors) >= 2:
                    lines.append(f"if ({label}) then (да)")
                else:
                    lines.append(f"if ({label}) then (yes)")
            elif node_type == 'process':
                lines.append(f":{label};")
            else:
                lines.append(f":{label};")
        
        for source, target in graph.edges():
            edge_label = graph.edges[source, target].get('label', '')
            source_type = graph.nodes[source].get('type', 'process')
            
            if source_type == 'decision':
                if edge_label and 'нет' in edge_label.lower():
                    lines.append(f"else (нет)")
                elif edge_label and 'no' in edge_label.lower():
                    lines.append(f"else (no)")
        
        if any(graph.nodes[node].get('type') == 'decision' for node in graph.nodes()):
            lines.append("endif")
        
        lines.append("")
        lines.append("@enduml")
        
        return '\n'.join(lines)
    
    def _generate_mermaid(self, graph: nx.DiGraph) -> str:
        lines = ["flowchart TD"]
        lines.append("")
        
        node_mapping = {}
        for idx, node in enumerate(graph.nodes()):
            node_id = f"n{idx}"
            node_mapping[node] = node_id
            
            node_type = graph.nodes[node].get('type', 'process')
            label = graph.nodes[node].get('label', node)
            
            if node_type == 'start':
                lines.append(f"    {node_id}([{label}])")
            elif node_type == 'end':
                lines.append(f"    {node_id}([{label}])")
            elif node_type == 'decision':
                lines.append(f"    {node_id}{{{{{label}}}}}")
            elif node_type == 'process':
                lines.append(f"    {node_id}[{label}]")
            elif node_type == 'data':
                lines.append(f"    {node_id}[/{label}/]")
            else:
                lines.append(f"    {node_id}[{label}]")
        
        lines.append("")
        
        for source, target in graph.edges():
            source_id = node_mapping[source]
            target_id = node_mapping[target]
            edge_label = graph.edges[source, target].get('label', '')
            
            if edge_label:
                lines.append(f"    {source_id} -->|{edge_label}| {target_id}")
            else:
                lines.append(f"    {source_id} --> {target_id}")
        
        lines.append("")
        
        for node in graph.nodes():
            node_type = graph.nodes[node].get('type', 'process')
            node_id = node_mapping[node]
            
            if node_type == 'start':
                lines.append(f"    style {node_id} fill:#90EE90,stroke:#228B22")
            elif node_type == 'end':
                lines.append(f"    style {node_id} fill:#FFB6C1,stroke:#DC143C")
            elif node_type == 'decision':
                lines.append(f"    style {node_id} fill:#FFD700,stroke:#FF8C00")
            elif node_type == 'process':
                lines.append(f"    style {node_id} fill:#87CEEB,stroke:#4682B4")
        
        return '\n'.join(lines)
    
    def generate_both(self, graph: nx.DiGraph) -> dict:
        return {
            'plantuml': self._generate_plantuml(graph),
            'mermaid': self._generate_mermaid(graph)
        }
