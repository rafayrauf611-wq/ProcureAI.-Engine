from celery import shared_task
from documents.models import Document
from documents.extractors import DocumentExtractor
from documents.classifiers import DocumentClassifier
from documents.validators import ValidationEngine
from procurement.workflow import AutomationWorkflow
from ai.client import AIClientFactory
from ai.parser import load_prompt
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_uploaded_document(self, document_id: int):
    try:
        document = Document.objects.get(id=document_id)
        
        # 1. Extraction & Classification
        raw_text = DocumentExtractor.extract_text(document.file.path)
        document.document_type = DocumentClassifier.classify_document(raw_text)
        document.save(update_fields=['document_type'])
        
        # 2. AI Parsing
        ai_client = AIClientFactory.get_client()
        extraction_prompt = load_prompt("extraction_prompt.txt")
        extracted_json = ai_client.extract_structured_data(raw_text, extraction_prompt)
        
        document.extracted_data = extracted_json
        document.save(update_fields=['extracted_data'])
        
        # 3. Validation
        validator = ValidationEngine(document, extracted_json)
        is_valid = validator.validate()
        
        # 4. Automate ERP Entry if Valid
        if is_valid:
            AutomationWorkflow.execute_post_validation(document)
            
    except Exception as exc:
        logger.error(f"Pipeline failed for doc {document_id}: {exc}")
        document = Document.objects.get(id=document_id)
        document.status = 'REJECTED'
        document.validation_errors = [{"error": str(exc)}]
        document.save()
        raise self.retry(exc=exc, countdown=60)
