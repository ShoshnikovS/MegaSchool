from fastapi import APIRouter, File, UploadFile
import time

from src.core.logger import app_logger
from src.core.exceptions import ImageProcessingError, ValidationError
from src.api.models.responses import UnifiedResponse
from src.utils.image_utils import bytes_to_numpy
from src.preprocessing.image_preprocessor import ImagePreprocessor
from src.ml_pipeline.detector import DiagramDetector
from src.ml_pipeline.ocr import TextRecognizer
from src.ml_pipeline.graph_constructor import GraphConstructor
from src.ml_pipeline.semantic_interpreter import SemanticInterpreter
from src.postprocessing.formatter import ResponseFormatter
from src.postprocessing.template_engine import TemplateEngine

router = APIRouter()

preprocessor = ImagePreprocessor()
detector = DiagramDetector()
ocr = TextRecognizer()
graph_constructor = GraphConstructor()
semantic_interpreter = SemanticInterpreter()
formatter = ResponseFormatter()
template_engine = TemplateEngine()


@router.post("/analyze", response_model=UnifiedResponse)
async def analyze_diagram(image: UploadFile = File(...)):
    start_time = time.time()
    
    app_logger.info(f"Received analyze request: {image.filename}")
    
    if not image.content_type.startswith("image/"):
        raise ValidationError(
            "Invalid file type. Only images are supported.",
            {"content_type": image.content_type}
        )
    
    try:
        image_bytes = await image.read()
        
        if len(image_bytes) > 10 * 1024 * 1024:
            raise ValidationError(
                "Image too large. Maximum size is 10MB.",
                {"size": len(image_bytes)}
            )
        
        app_logger.info(f"Image size: {len(image_bytes)} bytes")
        
        image_array = bytes_to_numpy(image_bytes)
        app_logger.debug(f"Converted to numpy array: {image_array.shape}")
        
        preprocessed_image = preprocessor.preprocess(image_array, enhance=True, denoise=False)
        app_logger.info("Image preprocessed")
        
        bboxes = detector.detect_diagram_elements(preprocessed_image)
        app_logger.info(f"Detected {len(bboxes)} diagram elements")
        
        texts = ocr.recognize_in_bboxes(preprocessed_image, bboxes)
        app_logger.info(f"Recognized text in {len(texts)} bounding boxes")
        
        graph = graph_constructor.construct_with_flow_analysis(bboxes, texts)
        app_logger.info(f"Constructed graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        
        interpretation = semantic_interpreter.interpret(graph)
        app_logger.info("Graph interpreted")
        
        description = template_engine.render_description(graph)
        app_logger.info("Description generated")
        
        processing_time = time.time() - start_time
        
        response = formatter.format_analyze_response(
            graph=graph,
            description=description,
            processing_time=processing_time,
            metadata={
                "image_filename": image.filename,
                "image_size_bytes": len(image_bytes),
                "num_detected_elements": len(bboxes),
                "flow_type": interpretation.get('flow_type', 'unknown')
            }
        )
        
        response = formatter.add_detected_elements(response, bboxes, texts)
        
        app_logger.info(f"Analysis completed in {processing_time:.2f}s")
        
        return response
        
    except ValidationError:
        raise
    except Exception as e:
        app_logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise ImageProcessingError(
            "Failed to process image",
            {"error": str(e)}
        )
