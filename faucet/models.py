from django.db import models
from django.utils import timezone

class FaucetRequest(models.Model):
    wallet_address = models.CharField(max_length=42)  # Adjust max_length as needed
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)

    @classmethod
    def has_recent_request(cls, wallet_address, ip_address):
        # Check if the wallet or IP has requested a token today
        today_start = timezone.now().date()
        return cls.objects.filter(
            models.Q(wallet_address=wallet_address) | models.Q(ip_address=ip_address),
            timestamp__gte=today_start
        ).exists()

    def __str__(self):
        return f"{self.wallet_address} - {self.ip_address} - {self.timestamp}"
