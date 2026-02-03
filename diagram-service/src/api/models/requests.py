from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class AnalyzeRequest(BaseModel):
    image_base64: Optional[str] = Field(
        None,
        description="Base64 encoded image string"
    )
    
    @field_validator('image_base64')
    @classmethod
    def validate_base64(cls, v):
        if v and len(v) > 15000000:
            raise ValueError("Image too large (max 15MB base64)")
        return v


class GenerateRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Text description of the algorithm/process",
        examples=["Начало. Проверить условие X. Если истина, выполнить действие A, иначе действие B. Конец."]
    )
    
    output_format: Literal["image", "code", "both"] = Field(
        default="both",
        description="Output format: image (PNG), code (PlantUML/Mermaid), or both"
    )
    
    diagram_type: Literal["flowchart", "bpmn", "uml"] = Field(
        default="flowchart",
        description="Type of diagram to generate"
    )
    
    layout: Literal["vertical", "horizontal", "auto"] = Field(
        default="auto",
        description="Layout direction for the diagram"
    )
