from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Project, Innovation, Contribution, Reward_Payment, Investment_Payment
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
class InvestmentPaymentAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_sent',)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Innovation, InnovationAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(Reward_Payment, RewardPaymentAdmin)
admin.site.register(Investment_Payment, InvestmentPaymentAdmin)