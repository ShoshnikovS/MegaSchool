import base64
import time
from typing import Dict, Any, Optional
import networkx as nx

from src.core.logger import app_logger
from src.api.models.responses import UnifiedResponse, GraphRepresentation, Artifacts, NodeRepresentation, EdgeRepresentation


class ResponseFormatter:
    def __init__(self):
        app_logger.info("ResponseFormatter initialized")
    
    def format_analyze_response(
        self,
        graph: nx.DiGraph,
        description: str,
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UnifiedResponse:
        try:
            graph_repr = self._graph_to_representation(graph)
            
            response = UnifiedResponse(
                task_type="image_to_text",
                description=description,
                graph_representation=graph_repr,
                artifacts=Artifacts(),
                processing_time_sec=round(processing_time, 2),
                metadata=metadata or {}
            )
            
            app_logger.debug("Formatted analyze response")
            return response
            
        except Exception as e:
            app_logger.error(f"Failed to format analyze response: {str(e)}")
            raise
    
    def format_generate_response(
        self,
        graph: nx.DiGraph,
        description: str,
        diagram_image: Optional[bytes] = None,
        diagram_code: Optional[str] = None,
        processing_time: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UnifiedResponse:
        try:
            graph_repr = self._graph_to_representation(graph)
            
            artifacts = Artifacts()
            
            if diagram_image:
                artifacts.diagram_image_base64 = base64.b64encode(diagram_image).decode('utf-8')
                app_logger.debug(f"Encoded diagram image: {len(diagram_image)} bytes")
            
            if diagram_code:
                artifacts.diagram_code = diagram_code
                app_logger.debug(f"Added diagram code: {len(diagram_code)} chars")
            
            response = UnifiedResponse(
                task_type="text_to_diagram",
                description=description,
                graph_representation=graph_repr,
                artifacts=artifacts,
                processing_time_sec=round(processing_time, 2),
                metadata=metadata or {}
            )
            
            app_logger.debug("Formatted generate response")
            return response
            
        except Exception as e:
            app_logger.error(f"Failed to format generate response: {str(e)}")
            raise
    
    def _graph_to_representation(self, graph: nx.DiGraph) -> GraphRepresentation:
        nodes = []
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]
            
            node_repr = NodeRepresentation(
                id=node_id,
                type=node_data.get('type', 'process'),
                label=node_data.get('label', ''),
                position=node_data.get('position', None)
            )
            nodes.append(node_repr)
        
        edges = []
        for source, target in graph.edges():
            edge_data = graph.edges[source, target]
            
            edge_repr = EdgeRepresentation(
                source=source,
                target=target,
                label=edge_data.get('label', None)
            )
            edges.append(edge_repr)
        
        return GraphRepresentation(nodes=nodes, edges=edges)
    
    def add_detected_elements(
        self,
        response: UnifiedResponse,
        bboxes: list,
        texts: Dict[int, str]
    ) -> UnifiedResponse:
        detected_elements = []
        
        for idx, bbox in enumerate(bboxes):
            element = {
                "id": idx,
                "bbox": bbox.to_dict() if hasattr(bbox, 'to_dict') else bbox,
                "text": texts.get(idx, "")
            }
            detected_elements.append(element)
        
        if response.artifacts is None:
            response.artifacts = Artifacts()
        
        response.artifacts.detected_elements = detected_elements
        
        app_logger.debug(f"Added {len(detected_elements)} detected elements to response")
        return response
