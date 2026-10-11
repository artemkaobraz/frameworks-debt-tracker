from django.urls import path

from . import views


urlpatterns = [
    path("", views.students, name="students"),
    path("<str:student_id>/", views.student_detail, name="student_detail"),
]
