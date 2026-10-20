from django.urls import path

from . import views


app_name = "students"


urlpatterns = [
    path("", views.students, name="list"),
    path("clean/", views.clean_students, name="clean"),
    path("<int:student_id>/", views.student_detail, name="detail"),
]
