from ai.client import AIClientFactory
from ai.parser import load_prompt
import logging

logger = logging.getLogger(__name__)

class DocumentClassifier:
    @staticmethod
    def classify_document(raw_text: str) -> str:
        """
        Uses a lightweight prompt to categorize the document type.
        """
        ai_client = AIClientFactory.get_client()
        prompt = load_prompt("classification_prompt.txt")
        
        try:
            # Expected JSON: {"document_type": "INVOICE", "confidence": 98}
            result = ai_client.extract_structured_data(raw_text, prompt)
            doc_type = result.get("document_type", "UNKNOWN").upper()
            
            valid_types = ['INVOICE', 'PO', 'QUOTATION', 'RFQ', 'DELIVERY_CHALLAN', 'GRN', 'CONTRACT']
            return doc_type if doc_type in valid_types else 'UNKNOWN'
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "UNKNOWN"
