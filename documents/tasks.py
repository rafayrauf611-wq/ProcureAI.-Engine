from celery import shared_task
from ai.client import AIClientFactory
from ai.parser import load_prompt
from documents.extractors import DocumentExtractor
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_uploaded_document(self, document_id: int, file_path: str):
    """
    Celery task to handle OCR and AI Extraction asynchronously.
    """
    try:
        # 1. Extract raw text via Plumber/PaddleOCR
        raw_text = DocumentExtractor.extract_text(file_path)
        
        # 2. Initialize the AI Client
        ai_client = AIClientFactory.get_client()
        extraction_prompt = load_prompt("extraction_prompt.txt")
        
        # 3. Extract Structured JSON
        structured_data = ai_client.extract_structured_data(raw_text, extraction_prompt)
        
        # 4. Save to database (Next phase)
        logger.info(f"Successfully extracted data for Document ID: {document_id}")
        return structured_data

    except Exception as exc:
        logger.warning(f"Task failed, retrying... Exception: {exc}")
        raise self.retry(exc=exc, countdown=60)
