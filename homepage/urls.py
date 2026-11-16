from django.urls import path

from . import views


app_name = "homepage"


urlpatterns = [
    path("", views.index, name="index"),
    path("disciplines/", views.disciplines, name="disciplines"),
    path("disciplines/new/", views.DisciplineCreateView.as_view(),
         name="discipline_create"),
    path("disciplines/<int:pk>/edit/",
         views.DisciplineUpdateView.as_view(), name="discipline_edit"),
    path("disciplines/<int:pk>/delete/",
         views.DisciplineDeleteView.as_view(), name="discipline_delete"),
]
