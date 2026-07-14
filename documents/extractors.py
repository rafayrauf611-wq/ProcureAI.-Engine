import os
import pdfplumber
from PIL import Image
from paddleocr import PaddleOCR
import logging

logger = logging.getLogger(__name__)

# Initialize PaddleOCR globally to prevent reloading the model on every call
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

class DocumentExtractor:
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return cls._extract_from_pdf(file_path)
        elif ext in ['.png', '.jpg', '.jpeg']:
            return cls._extract_from_image(file_path)
        elif ext in ['.docx', '.txt', '.xlsx', '.csv']:
            # Placeholders for standard python-docx / openpyxl logic
            return f"Extracted text from standard document: {ext}"
        else:
            raise ValueError(f"Unsupported document type: {ext}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                    else:
                        # Fallback to OCR if PDF page is an image
                        logger.info("No text layer found in PDF page, falling back to OCR.")
                        # Implementation detail: convert page to image and run through PaddleOCR
        except Exception as e:
            logger.error(f"PDF Extraction failed for {file_path}: {e}")
            raise
        return text

    @staticmethod
    def _extract_from_image(file_path: str) -> str:
        try:
            result = ocr_engine.ocr(file_path, cls=True)
            extracted_text = ""
            if result and result[0]:
                for line in result[0]:
                    extracted_text += line[1][0] + "\n"
            return extracted_text
        except Exception as e:
            logger.error(f"OCR Extraction failed for {file_path}: {e}")
            raise
