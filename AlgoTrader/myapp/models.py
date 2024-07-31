# myapp/models.py

from django.db import models
from django.core.exceptions import ValidationError

class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    stock1 = models.CharField(max_length=255)
    stock2 = models.CharField(max_length=255)
    quantity = models.IntegerField()
    entry = models.DecimalField(max_digits=10, decimal_places=2)
    entry_diff = models.CharField(max_length=10)
    exit = models.DecimalField(max_digits=10, decimal_places=2,  null=True, blank=True)
    exit_diff = models.CharField(max_length=10)
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2,  null=True, blank=True)
    stop_loss_diff = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Pending') # Pending, Placed, Exited
    order_ids = models.JSONField(default=list)  # Store order IDs as a JSON list
    alerts_sent = models.JSONField(default=list)  # Store a list of alerts sent

    def __str__(self):
        return f"{self.stock1} & {self.stock2} - {self.quantity} units"

    def clean(self):
        if self.entry <= 0 or self.quantity <= 0 :
            raise ValidationError("Entry, and Quantity must be positive numbers.")

    def save(self, *args, **kwargs):
        # Call the clean method before saving
        self.clean()
        super().save(*args, **kwargs)
    
    def add_alert(self, alert):
        if alert not in self.alerts_sent:
            self.alerts_sent.append(alert)
            self.save()
    
    def add_orderid(self, orderid):
        if orderid not in self.order_ids:
            self.order_ids.append(orderid)
            self.save()