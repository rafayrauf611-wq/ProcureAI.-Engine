import django_filters
from documents.models import Document
from procurement.models import PurchaseOrder

class DocumentFilter(django_filters.FilterSet):
    date_from = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    
    class Meta:
        model = Document
        fields = ['document_type', 'status', 'original_filename']

class PurchaseOrderFilter(django_filters.FilterSet):
    min_amount = django_filters.NumberFilter(field_name="total_amount", lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name="total_amount", lookup_expr='lte')
    supplier_name = django_filters.CharFilter(field_name='supplier__name', lookup_expr='icontains')

    class Meta:
        model = PurchaseOrder
        fields = ['status', 'supplier']
