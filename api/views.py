from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from documents.models import Document
from inventory.models import Item
from suppliers.models import Supplier
from procurement.models import PurchaseOrder, Quotation, Demand, GoodsReceiptNote
from procurement.services import ProcurementService
from documents.tasks import process_uploaded_document

from .serializers import (
    DocumentSerializer, DocumentUploadSerializer, ItemSerializer, 
    SupplierSerializer, PurchaseOrderSerializer, QuotationSerializer
)

# --- Standard GET Endpoints (Read-Only ViewSets) ---

class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer

class SupplierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class PurchaseOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class QuotationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer


# --- Action Endpoints (POST) ---

class DocumentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """POST /upload - Uploads a document and triggers async AI extraction."""
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            
            # Create Document record
            document = Document.objects.create(
                file=uploaded_file,
                original_filename=uploaded_file.name,
                uploader=request.user if request.user.is_authenticated else None,
                status='PENDING'
            )
            
            # Dispatch Celery Task for OCR & AI Extraction
            process_uploaded_document.delay(document.id)
            
            return Response(
                {"message": "File uploaded successfully. AI extraction started.", "document_id": document.id}, 
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GeneratePurchaseOrderView(APIView):
    def post(self, request, *args, **kwargs):
        """POST /generate-po - Generates a PO from a Demand using the Service Layer."""
        demand_id = request.data.get('demand_id')
        try:
            demand = Demand.objects.get(id=demand_id)
            po = ProcurementService.generate_purchase_order(demand)
            return Response(
                {"message": "Purchase Order generated.", "po_id": po.id}, 
                status=status.HTTP_201_CREATED
            )
        except Demand.DoesNotExist:
            return Response({"error": "Demand not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ThreeWayMatchView(APIView):
    def post(self, request, *args, **kwargs):
        """POST /three-way-match - Triggers the three-way match logic."""
        grn_id = request.data.get('grn_id')
        try:
            grn = GoodsReceiptNote.objects.get(id=grn_id)
            is_matched = ProcurementService.execute_three_way_match(grn)
            
            if is_matched:
                return Response({"message": "Three-way match successful. Invoice marked as paid."}, status=status.HTTP_200_OK)
            return Response({"error": "Three-way match failed due to discrepancies."}, status=status.HTTP_409_CONFLICT)
            
        except GoodsReceiptNote.DoesNotExist:
            return Response({"error": "GRN not found."}, status=status.HTTP_404_NOT_FOUND)
