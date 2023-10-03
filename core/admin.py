from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Project, Innovation, Contribution, Reward_Payment, Make_Investment, Receipt
# Register your models here.
class ProjectAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)

class InnovationAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)

class ContributionAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)
class Nested_ContributionAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)
class RewardPaymentAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_sent',)
class MakeInvestmentAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_sent',)
class ReceiptAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_generated',)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Innovation, InnovationAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(Reward_Payment, RewardPaymentAdmin)
admin.site.register(Make_Investment, MakeInvestmentAdmin)
admin.site.register(Receipt, ReceiptAdmin)