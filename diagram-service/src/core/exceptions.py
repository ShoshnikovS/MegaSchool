class DiagramServiceException(Exception):
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ImageProcessingError(DiagramServiceException):
    pass


class ModelLoadError(DiagramServiceException):
    pass


class DetectionError(DiagramServiceException):
    pass


class OCRError(DiagramServiceException):
    pass


class GraphConstructionError(DiagramServiceException):
    pass


class TextParsingError(DiagramServiceException):
    pass


class VisualizationError(DiagramServiceException):
    pass


class ValidationError(DiagramServiceException):
    pass


class ConfigurationError(DiagramServiceException):
    pass
