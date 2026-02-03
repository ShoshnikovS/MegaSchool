from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
import networkx as nx
from typing import Dict, Any

from src.core.logger import app_logger
from src.core.config import settings


class TemplateEngine:
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or str(settings.templates_path)
        
        try:
            self.env = Environment(
                loader=FileSystemLoader(self.template_dir),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
            app_logger.info(f"TemplateEngine initialized with template_dir={self.template_dir}")
        except Exception as e:
            app_logger.warning(f"Failed to load templates from {self.template_dir}: {str(e)}")
            self.env = None
    
    def render_description(self, graph: nx.DiGraph) -> str:
        try:
            context = self._prepare_graph_context(graph)
            
            if self.env:
                try:
                    template = self.env.get_template('algorithm_description.j2')
                    description = template.render(**context)
                    app_logger.debug("Rendered description using Jinja2 template")
                    return description
                except Exception as e:
                    app_logger.warning(f"Template rendering failed: {str(e)}, using fallback")
            
            description = self._render_fallback(context)
            return description
            
        except Exception as e:
            app_logger.error(f"Description rendering failed: {str(e)}")
            return "Не удалось сгенерировать описание алгоритма."
    
    def _prepare_graph_context(self, graph: nx.DiGraph) -> Dict[str, Any]:
        nodes_data = []
        for node in graph.nodes():
            node_info = {
                'id': node,
                'type': graph.nodes[node].get('type', 'process'),
                'label': graph.nodes[node].get('label', ''),
                'level': graph.nodes[node].get('level', 0)
            }
            nodes_data.append(node_info)
        
        nodes_data.sort(key=lambda n: n['level'])
        
        edges_data = []
        for source, target in graph.edges():
            edge_info = {
                'source': source,
                'target': target,
                'label': graph.edges[source, target].get('label', '')
            }
            edges_data.append(edge_info)
        
        start_nodes = [n for n in nodes_data if n['type'] == 'start']
        end_nodes = [n for n in nodes_data if n['type'] == 'end']
        decision_nodes = [n for n in nodes_data if n['type'] == 'decision']
        process_nodes = [n for n in nodes_data if n['type'] == 'process']
        
        return {
            'nodes': nodes_data,
            'edges': edges_data,
            'start_nodes': start_nodes,
            'end_nodes': end_nodes,
            'decision_nodes': decision_nodes,
            'process_nodes': process_nodes,
            'num_nodes': len(nodes_data),
            'num_edges': len(edges_data),
            'has_branches': len(decision_nodes) > 0
        }
    
    def _render_fallback(self, context: Dict[str, Any]) -> str:
        parts = []
        
        if context['start_nodes']:
            start_label = context['start_nodes'][0]['label']
            if start_label:
                parts.append(f"Алгоритм начинается: {start_label}.")
            else:
                parts.append("Алгоритм начинается.")
        
        for node in context['process_nodes']:
            label = node['label']
            if label:
                parts.append(f"Выполняется: {label}.")
        
        for node in context['decision_nodes']:
            label = node['label']
            if label:
                parts.append(f"Проверяется условие: {label}.")
        
        if context['end_nodes']:
            end_label = context['end_nodes'][0]['label']
            if end_label:
                parts.append(f"Алгоритм завершается: {end_label}.")
            else:
                parts.append("Алгоритм завершается.")
        
        if context['has_branches']:
            parts.append("Алгоритм содержит ветвления и условные переходы.")
        
        return ' '.join(parts)
    
    def render_from_string(self, template_string: str, **kwargs) -> str:
        try:
            template = Template(template_string)
            return template.render(**kwargs)
        except Exception as e:
            app_logger.error(f"String template rendering failed: {str(e)}")
            return ""
