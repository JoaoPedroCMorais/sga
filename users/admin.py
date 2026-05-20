from django.contrib import admin
from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    # As colunas que vão aparecer na tabela do painel
    list_display = ("email", "role", "is_staff", "is_superuser", "is_active")

    # Filtros laterais para facilitar a busca
    list_filter = ("role", "is_staff", "is_active")

    # Barra de pesquisa
    search_fields = ("email",)

    # Ordem padrão
    ordering = ("email",)
