import pghistory
from django.db import models
from django.conf import settings


@pghistory.track(
    pghistory.InsertEvent("class_created"),
    pghistory.UpdateEvent("class_updated"),
    pghistory.DeleteEvent("class_deleted"),
)
class ClassGroup(models.Model):
    """Turmas do curso (ex: Extensivo Manhã, Turma ITA)."""

    name = models.CharField("Nome da Turma", max_length=100, unique=True)
    year = models.IntegerField("Ano Letivo")
    is_active = models.BooleanField("Ativa", default=True)

    # Relação com professores (Muitos para Muitos)
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"role": "PROFESSOR"},
        related_name="teaching_classes",
        blank=True,
    )

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["-year", "name"]

    def __str__(self):
        return f"{self.name} ({self.year})"


@pghistory.track(
    pghistory.InsertEvent("student_created"), pghistory.UpdateEvent("student_updated")
)
class Student(models.Model):
    """Cadastro do Aluno."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "ALUNO"},
        related_name="student_profile",
    )
    enrollment_number = models.CharField(
        "Matrícula", max_length=20, unique=True, db_index=True
    )
    full_name = models.CharField("Nome Completo", max_length=200)
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.PROTECT,  # NUNCA apaga aluno se apagar a turma
        related_name="students",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.enrollment_number} - {self.full_name}"
