import pghistory
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


@pghistory.track(
    pghistory.InsertEvent("attendance_created"),
    pghistory.UpdateEvent("attendance_updated"),
    pghistory.DeleteEvent("attendance_deleted"),
)
class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", _("Presente")
        ABSENT = "ABSENT", _("Ausente")
        JUSTIFIED = "JUSTIFIED", _("Justificado")

    class Period(models.TextChoices):
        BEFORE_BREAK = "BEFORE_BREAK", _("Antes do Intervalo")
        AFTER_BREAK = "AFTER_BREAK", _("Depois do Intervalo")

    student = models.ForeignKey(
        "academic.Student",
        on_delete=models.PROTECT,
        related_name="attendance_records",
        verbose_name=_("aluno"),
        db_index=True,
    )
    date = models.DateField(_("data"), db_index=True)
    period = models.CharField(
        _("período"),
        max_length=12,
        choices=Period.choices,
    )
    status = models.CharField(
        _("status"),
        max_length=10,
        choices=Status.choices,
        default=Status.ABSENT,
    )
    observer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_attendances",
        verbose_name=_("monitor"),
        limit_choices_to={"role__in": ["MONITOR", "COORDENADOR"]},
        db_index=True,
    )
    created_at = models.DateTimeField(_("criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("registro de chamada")
        verbose_name_plural = _("registros de chamada")
        ordering = ["-date", "student"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date", "period"],
                name="unique_attendance_per_student_per_day_per_period",
            )
        ]

    def __str__(self) -> str:
        return f"{self.student} — {self.date} — {self.get_period_display()} — {self.get_status_display()}"


@pghistory.track(
    pghistory.InsertEvent("justification_created"),
    pghistory.UpdateEvent("justification_updated"),
    pghistory.DeleteEvent("justification_deleted"),
)
class AbsenceJustification(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pendente")
        APPROVED = "APPROVED", _("Aprovado")
        REJECTED = "REJECTED", _("Rejeitado")

    student = models.ForeignKey(
        "academic.Student",
        on_delete=models.PROTECT,
        related_name="justifications",
        verbose_name=_("aluno"),
        db_index=True,
    )
    date = models.DateField(_("data da falta"), db_index=True)
    reason = models.TextField(_("motivo"))
    file_url = models.URLField(_("comprovante (URL)"), blank=True)
    status = models.CharField(
        _("status"),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_justifications",
        verbose_name=_("revisor"),
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(_("criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("justificativa de falta")
        verbose_name_plural = _("justificativas de falta")
        ordering = ["-date", "student"]

    def __str__(self) -> str:
        return f"{self.student} — {self.date} — {self.get_status_display()}"
