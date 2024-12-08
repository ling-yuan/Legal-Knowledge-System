from django.contrib import admin
from .models import Law_Information, Local_Law_Information


# @admin.register(Law_Information)
# class LawInformationAdmin(admin.ModelAdmin):
#     list_display = ["name", "classification", "office", "status", "publish"]
#     list_filter = ["classification", "status"]
#     search_fields = ["name", "office"]
#     ordering = ["-publish"]


# @admin.register(Local_Law_Information)
# class LocalLawInformationAdmin(admin.ModelAdmin):
#     list_display = ["name", "classification", "office", "status", "publish"]
#     list_filter = ["classification", "status"]
#     search_fields = ["name", "office"]
#     ordering = ["-publish"]
