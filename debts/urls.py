from django.urls import path

from . import views


app_name = "debts"


urlpatterns = [
    path("", views.debts, name="list"),
    path("new/", views.DebtCreateView.as_view(), name="create"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:pk>/edit/", views.DebtUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.DebtDeleteView.as_view(), name="delete"),
    path("<int:debt_id>/", views.debt_detail, name="detail"),
]
