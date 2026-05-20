from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Manager customizado para o modelo User onde o email
    é o identificador único de autenticação, substituindo o username.
    """

    def create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        """Cria e retorna um usuário comum com email e senha."""
        if not email:
            raise ValueError(_("O campo email é obrigatório."))

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        """Cria e retorna um superusuário com email e senha."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superusuário precisa ter is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superusuário precisa ter is_superuser=True."))

        return self.create_user(email, password, **extra_fields)
