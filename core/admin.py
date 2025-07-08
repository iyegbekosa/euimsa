import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import AssociationFee, Payment, SkillAquisition


admin.site.register(AssociationFee)
admin.site.register(SkillAquisition)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'amount', 'ref', 'verified', 'date_created')
    list_filter = ('verified', 'level')
    search_fields = ('ref', 'email', 'user__username')
    actions = ['export_verified_payments']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(verified=True)  # Only show verified payments in admin

    def export_verified_payments(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="verified_payments.csv"'

        writer = csv.writer(response)
        writer.writerow(['User', 'Email', 'Level', 'Amount', 'Ref', 'Date Created'])

        for payment in queryset:
            writer.writerow([
                payment.user.username if payment.user else '',
                payment.email,
                payment.level,
                payment.amount,
                payment.ref,
                payment.date_created.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    export_verified_payments.short_description = "Export selected verified payments"
