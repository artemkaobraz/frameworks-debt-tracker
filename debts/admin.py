from django.contrib import admin

from .models import Debt


class StudentDebtInline(admin.TabularInline):
    model = Debt
    fk_name = "student"
    fields = ("discipline", "date_created", "is_closed")
    extra = 0
    verbose_name = "Задолженность"
    verbose_name_plural = "Задолженности"


class DisciplineDebtInline(admin.TabularInline):
    model = Debt
    fk_name = "discipline"
    fields = ("student", "date_created", "is_closed")
    extra = 0
    verbose_name = "Задолженность"
    verbose_name_plural = "Задолженности"


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student", "discipline", "date_created", "is_closed"
    )
    list_filter = ("is_closed", "date_created", "discipline")
    search_fields = ("student__name", "discipline__name")
    ordering = ("-date_created", "-id")
    list_select_related = ("student", "discipline")
    autocomplete_fields = ("student", "discipline")
