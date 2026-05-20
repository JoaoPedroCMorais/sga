from django.urls import path

from .views import TakeAttendanceView, toggle_attendance

app_name = "attendance"

urlpatterns = [
    # Rota concreta antes da paramétrica (boas práticas Django)
    path(
        "chamada/toggle/",
        toggle_attendance,
        name="toggle_attendance",
    ),
    path(
        "chamada/<int:class_group_id>/",
        TakeAttendanceView.as_view(),
        name="take_attendance",
    ),
]
