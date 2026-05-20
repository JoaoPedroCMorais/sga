from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import QuerySet
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from academic.models import ClassGroup, Student

from .models import AttendanceRecord

_ATTENDANCE_ROLES = {"MONITOR", "COORDENADOR"}


class TakeAttendanceView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Lista alunos de uma turma para o lançamento de chamada (GET)."""

    template_name = "attendance/take_attendance.html"
    context_object_name = "students"

    def test_func(self) -> bool:
        return self.request.user.role in _ATTENDANCE_ROLES

    def get_queryset(self) -> QuerySet[Student]:
        return (
            Student.objects.filter(class_group_id=self._class_group_id())
            .select_related("user", "class_group")
            .order_by("full_name")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["class_group"] = ClassGroup.objects.filter(
            pk=self._class_group_id()
        ).first()
        context["class_groups"] = ClassGroup.objects.filter(is_active=True).order_by(
            "name"
        )

        period = self._current_period()
        context["period"] = period
        context["period_choices"] = AttendanceRecord.Period.choices

        today = timezone.now().date()
        records_map: dict[int, AttendanceRecord] = {
            r.student_id: r
            for r in AttendanceRecord.objects.filter(
                student__in=self.object_list,
                date=today,
                period=period,
            )
        }
        context["student_rows"] = [
            (student, records_map.get(student.pk)) for student in self.object_list
        ]
        return context

    def _class_group_id(self) -> int | None:
        """Retorna o ID da turma vindo da URL ou do query param GET."""
        return self.kwargs.get("class_group_id") or self.request.GET.get(
            "class_group_id"
        )

    def _current_period(self) -> str:
        period = self.request.GET.get("period", AttendanceRecord.Period.BEFORE_BREAK)
        if period not in AttendanceRecord.Period.values:
            return AttendanceRecord.Period.BEFORE_BREAK
        return period


@login_required
@require_POST
def toggle_attendance(request: HttpRequest) -> HttpResponse:
    """
    Recebe POST do HTMX, persiste o registro de chamada e devolve o fragmento
    HTML dos botões atualizado.

    POST body:
        student_id  int              ID do aluno
        status      str              PRESENT | ABSENT | JUSTIFIED
        period      str              BEFORE_BREAK | AFTER_BREAK
    """
    if request.user.role not in _ATTENDANCE_ROLES:
        return HttpResponseForbidden()

    status = request.POST.get("status", "")
    if status not in AttendanceRecord.Status.values:
        return HttpResponseBadRequest("Status inválido.")

    period = request.POST.get("period", "")
    if period not in AttendanceRecord.Period.values:
        return HttpResponseBadRequest("Período inválido.")

    try:
        student_id = int(request.POST.get("student_id", ""))
    except (ValueError, TypeError):
        return HttpResponseBadRequest("student_id inválido.")

    student = get_object_or_404(
        Student.objects.select_related("class_group"), pk=student_id
    )

    record, _ = AttendanceRecord.objects.update_or_create(
        student=student,
        date=timezone.now().date(),
        period=period,
        defaults={"status": status, "observer": request.user},
    )

    return render(
        request,
        "attendance/partials/_attendance_button.html",
        {"student": student, "record": record, "period": period},
    )
