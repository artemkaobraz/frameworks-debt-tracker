from django import forms
from django.utils import timezone

from .models import Debt


class DebtFilterForm(forms.Form):
    q = forms.CharField(
        label="Поиск по студенту или дисциплине", required=False,
    )
    discipline = forms.CharField(
        label="Название дисциплины", required=False,
    )
    student_id = forms.IntegerField(
        label="ID студента", min_value=1, required=False,
    )
    discipline_id = forms.IntegerField(
        label="ID дисциплины", min_value=1, required=False,
    )
    date_from = forms.DateField(
        label="Дата с", required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        label="Дата по", required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    status = forms.ChoiceField(
        label="Статус", required=False,
        choices=(
            ("", "Все статусы"),
            ("open", "Активные"),
            ("closed", "Закрытые"),
        ),
    )
    sort = forms.ChoiceField(
        label="Сортировка", required=False,
        choices=(
            ("date", "По дате"),
            ("date_desc", "По дате, сначала новые"),
            ("student", "По студенту"),
            ("discipline", "По дисциплине"),
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            self.add_error("date_to", "Дата окончания раньше даты начала.")
        return cleaned_data


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ("student", "discipline", "date_created", "is_closed")
        widgets = {
            "date_created": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}
            ),
        }
        help_texts = {
            "date_created": "Укажите дату возникновения задолженности.",
            "is_closed": "Закрытая задолженность не считается активной.",
        }

    def clean_date_created(self):
        value = self.cleaned_data["date_created"]
        if value > timezone.localdate():
            raise forms.ValidationError(
                "Дата задолженности не может быть в будущем."
            )
        return value

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        discipline = cleaned_data.get("discipline")
        is_closed = cleaned_data.get("is_closed")
        if student and discipline and is_closed is False:
            duplicate = Debt.objects.open().filter(
                student=student, discipline=discipline
            ).exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError(
                    "У студента уже есть активная задолженность "
                    "по этой дисциплине."
                )
        return cleaned_data
