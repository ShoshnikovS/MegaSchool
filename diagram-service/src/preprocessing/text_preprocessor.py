import re
from typing import List

from src.core.logger import app_logger


class TextPreprocessor:
    def __init__(self):
        app_logger.info("TextPreprocessor initialized")
    
    def preprocess(self, text: str) -> str:
        try:
            app_logger.debug(f"Preprocessing text of length {len(text)}")
            
            processed = text.strip()
            
            processed = re.sub(r'\s+', ' ', processed)
            
            processed = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\\]', '', processed, flags=re.UNICODE)
            
            app_logger.debug(f"Text preprocessed. Output length: {len(processed)}")
            return processed
            
        except Exception as e:
            app_logger.error(f"Text preprocessing failed: {str(e)}")
            return text
    
    def clean_ocr_text(self, text: str) -> str:
        try:
            cleaned = text.strip()
            
            cleaned = re.sub(r'[^\w\s\.\,\-]', '', cleaned, flags=re.UNICODE)
            
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            return cleaned
            
        except Exception as e:
            app_logger.warning(f"OCR text cleaning failed: {str(e)}")
            return text
    
    def normalize_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
    
    def split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[\.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\b\w+\b', text.lower(), flags=re.UNICODE)
        
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'к', 'от', 'из', 'о', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
