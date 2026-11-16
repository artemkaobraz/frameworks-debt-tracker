from django.contrib import admin

from debts.admin import StudentDebtInline

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group_number", "record_book")
    list_filter = ("group_number",)
    search_fields = ("name", "group_number", "record_book")
    ordering = ("name", "id")
    inlines = (StudentDebtInline,)
