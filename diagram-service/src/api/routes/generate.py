from fastapi import APIRouter
import time

from src.core.logger import app_logger
from src.core.exceptions import TextParsingError, VisualizationError
from src.api.models.requests import GenerateRequest
from src.api.models.responses import UnifiedResponse
from src.preprocessing.text_preprocessor import TextPreprocessor
from src.generative_pipeline.text_parser import TextToGraphParser
from src.generative_pipeline.visualizer import GraphVisualizer
from src.generative_pipeline.code_generator import DiagramCodeGenerator
from src.postprocessing.formatter import ResponseFormatter
from src.postprocessing.template_engine import TemplateEngine

router = APIRouter()

text_preprocessor = TextPreprocessor()
text_parser = TextToGraphParser()
visualizer = GraphVisualizer()
code_generator = DiagramCodeGenerator()
formatter = ResponseFormatter()
template_engine = TemplateEngine()


@router.post("/generate", response_model=UnifiedResponse)
async def generate_diagram(request: GenerateRequest):
    start_time = time.time()
    
    app_logger.info(f"Received generate request: format={request.output_format}, type={request.diagram_type}")
    app_logger.debug(f"Description: {request.description[:100]}...")
    
    try:
        text_preprocessor, text_parser, visualizer, code_generator, formatter, template_engine = get_components()
        
        preprocessed_text = text_preprocessor.preprocess(request.description)
        app_logger.info("Text preprocessed")
        
        graph = text_parser.parse(preprocessed_text)
        app_logger.info(f"Parsed text into graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        
        diagram_image = None
        diagram_code = None
        
        if request.output_format in ["image", "both"]:
            layout_direction = 'vertical' if request.layout == 'vertical' else 'horizontal' if request.layout == 'horizontal' else 'vertical'
            diagram_image = visualizer.render(graph, layout=layout_direction, format='png', dpi=150)
            app_logger.info(f"Generated diagram image: {len(diagram_image)} bytes")
        
        if request.output_format in ["code", "both"]:
            diagram_code = code_generator.generate(graph, format='plantuml')
            app_logger.info(f"Generated PlantUML code: {len(diagram_code)} chars")
        
        description = template_engine.render_description(graph)
        app_logger.info("Description generated from graph")
        
        processing_time = time.time() - start_time
        
        response = formatter.format_generate_response(
            graph=graph,
            description=description,
            diagram_image=diagram_image,
            diagram_code=diagram_code,
            processing_time=processing_time,
            metadata={
                "output_format": request.output_format,
                "diagram_type": request.diagram_type,
                "layout": request.layout,
                "num_nodes": graph.number_of_nodes(),
                "num_edges": graph.number_of_edges()
            }
        )
        
        app_logger.info(f"Generation completed in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error generating diagram: {str(e)}", exc_info=True)
        raise VisualizationError(
            "Failed to generate diagram",
            {"error": str(e)}
        )
