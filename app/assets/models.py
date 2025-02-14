from django.db import models
from app.config.models import Option as OptionConfig
#from django.contrib.auth.models import User

from app.people.models import CustomUser


class Asset(models.Model):
    name = models.CharField(max_length=200)
    asset_id = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(OptionConfig , on_delete=models.CASCADE)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    warranty_expiration = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='assets/', null=True, blank=True)
    location = models.CharField(max_length=200)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.ForeignKey(OptionConfig ,on_delete=models.CASCADE, related_name='asset_status')

    def __str__(self):
        return f"{self.name} ({self.asset_id})"

    class Meta:
        verbose_name = 'Aset'
        verbose_name_plural = 'Aset'

class Maintenance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.ForeignKey(OptionConfig , on_delete=models.CASCADE, related_name='maintenance_type')
    maintenance_date = models.DateField()
    next_maintenance_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    performed_by = models.CharField(max_length=200)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Maintenance {self.maintenance_type} on {self.asset.name}"

class Depreciation(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='depreciation_records')
    depreciation_date = models.DateField()
    depreciation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Depreciation on {self.asset.name} - {self.depreciation_amount}"

class Inventory(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField()
    reorder_threshold = models.PositiveIntegerField()

    def __str__(self):
        return f"Inventory for {self.asset.name} - {self.stock_quantity} in stock"

class AssetLifecycle(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='lifecycle_records')
    stage = models.CharField(max_length=100)  # e.g., Acquisition, Maintenance, Disposal
    date = models.DateField()
    image = models.ImageField(upload_to='assets/lifecycle/', null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.stage} - {self.asset.name} on {self.date}"

class Compliance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='compliance_records')
    compliance_type = models.CharField(max_length=100)  # e.g., Safety, Environmental, Regulatory
    status = models.CharField(max_length=50)  # e.g., Compliant, Non-Compliant, Pending
    last_checked = models.DateField()
    next_check_due = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Compliance {self.compliance_type} for {self.asset.name}"

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

class Procurement(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='procurement_records')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    procurement_date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50)  # Paid, Pending, etc.

    def __str__(self):
        return f"Procurement for {self.asset.name} from {self.supplier.name}"

class AssetAssignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assigned_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Asset {self.asset.name} assigned to {self.user.username}"

