from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
import random
import string
from django.contrib.auth.hashers import make_password, check_password


def generate_gov_code():
    return "MED-" + ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=5)
    )


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    gov_code = models.CharField(max_length=100, unique=True, blank=True)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    license_document = models.FileField(upload_to="licenses/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def save(self, *args, **kwargs):
        if not self.gov_code:
            self.gov_code = generate_gov_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.gov_code})"


class Medicine(models.Model):
    tx_hash = models.CharField(max_length=66, unique=True, blank=True, null=True)  # blockchain transaction hash
    name = models.CharField(max_length=100)
    batch = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    expiry = models.DateField()
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.tx_hash})" if self.tx_hash else self.name


def save(self, *args, **kwargs):
    # Generate QR code only if tx_hash exists and qr_code is empty
    if self.tx_hash and not self.qr_code:
        from io import BytesIO
        from django.core.files import File
        import qrcode

        # Create the verification URL
        verify_url = f"http://127.0.0.1:8000/verify/result/?tx_hash={self.tx_hash}"

        # Generate QR code for the URL
        qr = qrcode.make(verify_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"{self.tx_hash}.png", File(buffer), save=False)

    super().save(*args, **kwargs)

