from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, SupplierViewSet, InventoryViewSet, 
    PurchaseOrderViewSet, QuotationViewSet,
    DocumentUploadView, GeneratePurchaseOrderView, ThreeWayMatchView
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')
router.register(r'quotations', QuotationViewSet, basename='quotations')

urlpatterns = [
    # Expose ViewSet GET endpoints
    path('', include(router.urls)),
    
    # Expose Action POST endpoints
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('generate-po/', GeneratePurchaseOrderView.as_view(), name='generate-po'),
    path('three-way-match/', ThreeWayMatchView.as_view(), name='three-way-match'),
]
