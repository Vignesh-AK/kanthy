from django.contrib import admin

# Register your models here.

admin.site.site_header = "Payment Admin"
admin.site.site_title = "Payment Admin Portal"
admin.site.index_title = "Welcome to the Payment Admin Portal"
from payment.models import Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'status')

    def has_add_permission(self, request):
        return False