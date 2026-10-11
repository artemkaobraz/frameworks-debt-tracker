from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("disciplines/", views.disciplines, name="disciplines"),
]
