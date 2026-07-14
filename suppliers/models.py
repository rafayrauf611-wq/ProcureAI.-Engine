from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=255) #[cite: 1]
    email = models.EmailField() #[cite: 1]
    
    class Meta:
        db_table = 'suppliers_supplier'
