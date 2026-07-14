from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

class DocumentAPITests(APITestCase):
    
    @patch('api.views.process_uploaded_document.delay')
    def test_document_upload_endpoint(self, mock_celery_task):
        url = reverse('document-upload')
        dummy_file = SimpleUploadedFile(
            "dummy_invoice.pdf", 
            b"file_content", 
            content_type="application/pdf"
        )
        
        response = self.client.post(url, {'file': dummy_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('document_id', response.data)
        
        # Verify the Celery task was successfully dispatched with the new document ID
        mock_celery_task.assert_called_once_with(response.data['document_id'])
