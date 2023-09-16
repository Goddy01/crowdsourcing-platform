from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Project, Innovation, Contribution
# Register your models here.
class ProjectAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)

class InnovationAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)

class ContributionAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Innovation, InnovationAdmin)
admin.site.register(Contribution, ContributionAdmin)