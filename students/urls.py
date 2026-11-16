from django.urls import path

from . import views


app_name = "students"


urlpatterns = [
    path("", views.students, name="list"),
    path("new/", views.StudentCreateView.as_view(), name="create"),
    path("clean/", views.clean_students, name="clean"),
    path("<int:pk>/edit/", views.StudentUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.StudentDeleteView.as_view(), name="delete"),
    path("<int:student_id>/", views.student_detail, name="detail"),
]
