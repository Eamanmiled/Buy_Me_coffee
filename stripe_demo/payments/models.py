from django.db import models

class Payment(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email or 'Unknown'} - ${self.amount/100:.2f} ({self.status})"
