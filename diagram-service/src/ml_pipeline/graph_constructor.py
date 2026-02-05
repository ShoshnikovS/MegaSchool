import networkx as nx
from typing import List, Dict, Any, Tuple
import numpy as np

from src.core.logger import app_logger
from src.core.exceptions import GraphConstructionError
from src.ml_pipeline.detector import BoundingBox
from src.utils.graph_utils import create_directed_graph, add_node, add_edge


class GraphConstructor:
    def __init__(self, vertical_threshold: float = 50.0, horizontal_threshold: float = 100.0):
        self.vertical_threshold = vertical_threshold
        self.horizontal_threshold = horizontal_threshold
        app_logger.info(f"GraphConstructor initialized with v_threshold={vertical_threshold}, h_threshold={horizontal_threshold}")
    
    def construct(self, bboxes: List[BoundingBox], texts: Dict[int, str]) -> nx.DiGraph:
        try:
            app_logger.debug(f"Constructing graph from {len(bboxes)} bounding boxes")
            
            graph = create_directed_graph()
            
            for idx, bbox in enumerate(bboxes):
                node_id = f"node_{idx}"
                text_obj = texts.get(idx, "")
                
                # Извлекаем текст из OCRResult если это объект
                if hasattr(text_obj, 'text'):
                    text = text_obj.text
                elif isinstance(text_obj, str):
                    text = text_obj
                else:
                    text = ""
                
                add_node(
                    graph,
                    node_id,
                    type=bbox.class_name,
                    label=text,
                    position=[bbox.center_x, bbox.center_y],
                    bbox=[bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                    confidence=bbox.confidence
                )
            
            self._connect_nodes(graph, bboxes)
            
            app_logger.info(f"Graph constructed: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
            return graph
            
        except Exception as e:
            app_logger.error(f"Graph construction failed: {str(e)}", exc_info=True)
            raise GraphConstructionError(f"Failed to construct graph: {str(e)}")
    
    def _connect_nodes(self, graph: nx.DiGraph, bboxes: List[BoundingBox]):
        nodes = list(graph.nodes())
        
        for i, node1 in enumerate(nodes):
            bbox1 = bboxes[i]
            
            for j, node2 in enumerate(nodes):
                if i == j:
                    continue
                
                bbox2 = bboxes[j]
                
                if self._should_connect(bbox1, bbox2):
                    add_edge(graph, node1, node2)
                    app_logger.debug(f"Connected {node1} -> {node2}")
    
    def _should_connect(self, bbox1: BoundingBox, bbox2: BoundingBox) -> bool:
        dx = bbox2.center_x - bbox1.center_x
        dy = bbox2.center_y - bbox1.center_y
        
        if dy > self.vertical_threshold and abs(dx) < self.horizontal_threshold:
            return True
        
        if dx > self.horizontal_threshold and abs(dy) < self.vertical_threshold:
            return True
        
        return False
    
    def construct_with_flow_analysis(self, bboxes: List[BoundingBox], texts: Dict[int, str]) -> nx.DiGraph:
        graph = self.construct(bboxes, texts)
        
        self._identify_start_end_nodes(graph, bboxes)
        
        self._refine_connections(graph, bboxes)
        
        return graph
    
    def _identify_start_end_nodes(self, graph: nx.DiGraph, bboxes: List[BoundingBox]):
        nodes = list(graph.nodes())
        
        if not nodes:
            return
        
        topmost_idx = min(range(len(bboxes)), key=lambda i: bboxes[i].center_y)
        topmost_node = nodes[topmost_idx]
        graph.nodes[topmost_node]['type'] = 'start'
        app_logger.debug(f"Identified start node: {topmost_node}")
        
        bottommost_idx = max(range(len(bboxes)), key=lambda i: bboxes[i].center_y)
        bottommost_node = nodes[bottommost_idx]
        graph.nodes[bottommost_node]['type'] = 'end'
        app_logger.debug(f"Identified end node: {bottommost_node}")
    
    def _refine_connections(self, graph: nx.DiGraph, bboxes: List[BoundingBox]):
        nodes = list(graph.nodes())
        
        for node in nodes:
            successors = list(graph.successors(node))
            
            if len(successors) > 1:
                node_type = graph.nodes[node].get('type', 'process')
                if node_type != 'decision':
                    graph.nodes[node]['type'] = 'decision'
                    app_logger.debug(f"Changed {node} to decision (multiple outputs)")
    
    def construct_from_coordinates(self, coordinates: List[Tuple[float, float]], labels: List[str]) -> nx.DiGraph:
        graph = create_directed_graph()
        
        for idx, (x, y) in enumerate(coordinates):
            node_id = f"node_{idx}"
            label = labels[idx] if idx < len(labels) else ""
            
            add_node(
                graph,
                node_id,
                type='process',
                label=label,
                position=[x, y]
            )
        
        sorted_indices = sorted(range(len(coordinates)), key=lambda i: (coordinates[i][1], coordinates[i][0]))
        
        for i in range(len(sorted_indices) - 1):
            current_idx = sorted_indices[i]
            next_idx = sorted_indices[i + 1]
            add_edge(graph, f"node_{current_idx}", f"node_{next_idx}")
        
        return graph
