import networkx as nx
from typing import Optional, Literal
import io
from PIL import Image
import numpy as np

from src.core.logger import app_logger
from src.core.exceptions import VisualizationError


class GraphVisualizer:
    def __init__(self):
        app_logger.info("GraphVisualizer initialized")
        
        self.node_styles = {
            'start': {
                'shape': 'ellipse',
                'style': 'filled',
                'fillcolor': '#90EE90',
                'color': '#228B22'
            },
            'end': {
                'shape': 'ellipse',
                'style': 'filled',
                'fillcolor': '#FFB6C1',
                'color': '#DC143C'
            },
            'process': {
                'shape': 'box',
                'style': 'filled',
                'fillcolor': '#87CEEB',
                'color': '#4682B4'
            },
            'decision': {
                'shape': 'diamond',
                'style': 'filled',
                'fillcolor': '#FFD700',
                'color': '#FF8C00'
            },
            'data': {
                'shape': 'parallelogram',
                'style': 'filled',
                'fillcolor': '#DDA0DD',
                'color': '#9370DB'
            }
        }
    
    def render(
        self,
        graph: nx.DiGraph,
        layout: Literal['vertical', 'horizontal', 'auto'] = 'vertical',
        format: str = 'png',
        dpi: int = 150
    ) -> bytes:
        try:
            app_logger.debug(f"Rendering graph with {graph.number_of_nodes()} nodes, layout={layout}")
            
            try:
                import pygraphviz as pgv
                use_pygraphviz = True
            except ImportError:
                app_logger.warning("pygraphviz not available, using matplotlib fallback")
                use_pygraphviz = False
            
            if use_pygraphviz:
                return self._render_with_pygraphviz(graph, layout, format, dpi)
            else:
                return self._render_with_matplotlib(graph, layout, format, dpi)
            
        except Exception as e:
            app_logger.error(f"Graph rendering failed: {str(e)}", exc_info=True)
            raise VisualizationError(f"Failed to render graph: {str(e)}")
    
    def _render_with_pygraphviz(
        self,
        graph: nx.DiGraph,
        layout: str,
        format: str,
        dpi: int
    ) -> bytes:
        import pygraphviz as pgv
        
        agraph = pgv.AGraph(directed=True, strict=False)
        
        agraph.graph_attr['dpi'] = str(dpi)
        agraph.graph_attr['rankdir'] = 'TB' if layout == 'vertical' else 'LR'
        agraph.graph_attr['bgcolor'] = 'white'
        agraph.graph_attr['splines'] = 'ortho'
        
        for node in graph.nodes():
            node_type = graph.nodes[node].get('type', 'process')
            label = graph.nodes[node].get('label', node)
            
            style = self.node_styles.get(node_type, self.node_styles['process'])
            
            agraph.add_node(
                node,
                label=label,
                **style
            )
        
        for source, target in graph.edges():
            edge_label = graph.edges[source, target].get('label', '')
            agraph.add_edge(source, target, label=edge_label)
        
        agraph.layout(prog='dot')
        
        image_bytes = agraph.draw(format=format)
        
        app_logger.info(f"Graph rendered successfully with pygraphviz")
        return image_bytes
    
    def _render_with_matplotlib(
        self,
        graph: nx.DiGraph,
        layout: str,
        format: str,
        dpi: int
    ) -> bytes:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        
        fig, ax = plt.subplots(figsize=(12, 8), dpi=dpi)
        
        if layout == 'vertical':
            pos = nx.spring_layout(graph, k=2, iterations=50)
        else:
            pos = nx.kamada_kawai_layout(graph)
        
        node_colors = []
        for node in graph.nodes():
            node_type = graph.nodes[node].get('type', 'process')
            style = self.node_styles.get(node_type, self.node_styles['process'])
            node_colors.append(style['fillcolor'])
        
        nx.draw_networkx_nodes(
            graph, pos,
            node_color=node_colors,
            node_size=3000,
            ax=ax
        )
        
        nx.draw_networkx_edges(
            graph, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            ax=ax
        )
        
        labels = {
            node: graph.nodes[node].get('label', node)[:30]
            for node in graph.nodes()
        }
        nx.draw_networkx_labels(
            graph, pos,
            labels,
            font_size=8,
            ax=ax
        )
        
        edge_labels = {
            (source, target): graph.edges[source, target].get('label', '')
            for source, target in graph.edges()
        }
        nx.draw_networkx_edge_labels(
            graph, pos,
            edge_labels,
            font_size=7,
            ax=ax
        )
        
        ax.axis('off')
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format=format, dpi=dpi, bbox_inches='tight')
        buffer.seek(0)
        image_bytes = buffer.read()
        plt.close(fig)
        
        app_logger.info(f"Graph rendered successfully with matplotlib")
        return image_bytes
    
    def render_to_image(self, graph: nx.DiGraph, **kwargs) -> Image.Image:
        image_bytes = self.render(graph, **kwargs)
        return Image.open(io.BytesIO(image_bytes))
    
    def render_to_numpy(self, graph: nx.DiGraph, **kwargs) -> np.ndarray:
        image = self.render_to_image(graph, **kwargs)
        return np.array(image)
