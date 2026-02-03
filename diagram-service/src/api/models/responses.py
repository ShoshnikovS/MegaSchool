from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal


class NodeRepresentation(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    type: str = Field(..., description="Node type: start, end, process, decision, data")
    label: str = Field(..., description="Node label/text")
    position: Optional[List[float]] = Field(None, description="[x, y] coordinates")


class EdgeRepresentation(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge label (for conditions)")


class GraphRepresentation(BaseModel):
    nodes: List[NodeRepresentation] = Field(default_factory=list)
    edges: List[EdgeRepresentation] = Field(default_factory=list)


class Artifacts(BaseModel):
    diagram_image_base64: Optional[str] = Field(None, description="Generated diagram as base64 PNG")
    diagram_code: Optional[str] = Field(None, description="Diagram code (PlantUML/Mermaid)")
    detected_elements: Optional[List[Dict[str, Any]]] = Field(None, description="Detected elements with bboxes")


class UnifiedResponse(BaseModel):
    task_type: Literal["image_to_text", "text_to_diagram"] = Field(
        ...,
        description="Type of task performed"
    )
    description: str = Field(
        ...,
        description="Human-readable description of the algorithm"
    )
    graph_representation: GraphRepresentation = Field(
        ...,
        description="Structured graph representation"
    )
    artifacts: Artifacts = Field(
        default_factory=Artifacts,
        description="Additional artifacts (images, code, etc.)"
    )
    processing_time_sec: float = Field(
        ...,
        description="Processing time in seconds"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    device: str = Field(..., description="Device being used (cpu/cuda)")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")
