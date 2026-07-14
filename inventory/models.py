from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255) #
    sku = models.CharField(max_length=50, unique=True) #
    current_stock = models.IntegerField(default=0) #[cite: 1]
    
    class Meta:
        db_table = 'inventory_items'
