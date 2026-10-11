from django.urls import path

from . import views


urlpatterns = [
    path("", views.debts, name="debts"),
    path("<str:debt_id>/", views.debt_detail, name="debt_detail"),
]
