from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import CustomUserManager


class User(AbstractUser):
    """
    Modelo de usuário customizado do SGA.
    Usa email como identificador único (sem campo username).
    """

    class Role(models.TextChoices):
        COORDENADOR = "COORDENADOR", _("Coordenador")
        PROFESSOR = "PROFESSOR", _("Professor")
        MONITOR = "MONITOR", _("Monitor")
        ALUNO = "ALUNO", _("Aluno")

    # Remove o campo username herdado de AbstractUser
    username = None

    email = models.EmailField(
        _("endereço de email"),
        unique=True,
        error_messages={
            "unique": _("Já existe um usuário cadastrado com este email."),
        },
    )

    role = models.CharField(
        _("perfil de acesso"),
        max_length=20,
        choices=Role.choices,
        default=Role.ALUNO,
        db_index=True,
    )

    # Define email como campo de login
    USERNAME_FIELD = "email"

    # Remove email de REQUIRED_FIELDS (já é obrigatório por ser USERNAME_FIELD)
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("usuário")
        verbose_name_plural = _("usuários")
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    # --- Métodos auxiliares de verificação de perfil ---

    @property
    def is_coordenador(self) -> bool:
        return self.role == self.Role.COORDENADOR

    @property
    def is_professor(self) -> bool:
        return self.role == self.Role.PROFESSOR

    @property
    def is_monitor(self) -> bool:
        return self.role == self.Role.MONITOR

    @property
    def is_aluno(self) -> bool:
        return self.role == self.Role.ALUNO
