from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "learner", "course", "amount", "status", "created_at")
    search_fields = ("reference", "learner__email", "course__title")
    list_filter = ("status", "provider")

# Register your models here.
