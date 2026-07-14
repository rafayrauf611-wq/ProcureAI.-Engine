from rest_framework import serializers
from documents.models import Document
from inventory.models import Item
from suppliers.models import Supplier
from procurement.models import PurchaseOrder, Quotation, Demand

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'original_filename', 'document_type', 'status', 'extracted_data', 'validation_errors', 'created_at']
        read_only_fields = ['document_type', 'status', 'extracted_data', 'validation_errors', 'created_at']

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['file']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'demand', 'supplier', 'supplier_name', 'total_amount', 'status']

class QuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = '__all__'
