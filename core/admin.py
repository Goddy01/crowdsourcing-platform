from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Project
# Register your models here.
class ProjectAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_created',)
admin.site.register(Project, ProjectAdmin)