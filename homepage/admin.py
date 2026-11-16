from django.contrib import admin

from debts.admin import DisciplineDebtInline

from .models import Discipline


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "teacher", "semester")
    list_filter = ("semester",)
    search_fields = ("name", "teacher")
    ordering = ("name", "id")
    inlines = (DisciplineDebtInline,)
