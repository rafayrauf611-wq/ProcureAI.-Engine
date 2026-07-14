from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import DocumentFilter, PurchaseOrderFilter

class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DocumentFilter
    # Enables full-text search across the JSON field and filename
    search_fields = ['original_filename', 'extracted_data__supplier__value', 'extracted_data__invoice_number__value']
    ordering_fields = ['created_at']

class PurchaseOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-id')
    serializer_class = PurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PurchaseOrderFilter
    search_fields = ['supplier__name', 'demand__requisition__item__sku']
