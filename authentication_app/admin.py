from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Medicine, Manufacturer

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        "tx_hash",
        "name",
        "batch",
        "manufacturer",
        "expiry",
    )

    search_fields = ("tx_hash", "name", "batch", "manufacturer")
    list_filter = ("expiry",)

    # REMOVE tx_hash from readonly to avoid system check error
    readonly_fields = ("tx_hash", "qr_code")


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "gov_code",
        "phone",
        "license_number",
        "is_verified",
        "created_at",
    )

    search_fields = ("name", "email", "gov_code", "license_number")
    list_filter = ("is_verified",)
    readonly_fields = ("gov_code", "created_at")

    fields = (
        "name",
        "email",
        "password_hash",
        "gov_code",
        "phone",
        "license_number",
        "license_document",
        "is_verified",
    )

    def save_model(self, request, obj, form, change):
        if not change or "password_hash" in form.changed_data:
            obj.password_hash = make_password(obj.password_hash)
        super().save_model(request, obj, form, change)
