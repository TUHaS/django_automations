from django.contrib import admin
from django.apps import apps
from import_export.admin import ImportExportActionModelAdmin

models = apps.get_models()
for model in models:
    try:
        admin.site.register(model, ImportExportActionModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass

