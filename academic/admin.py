from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from .models import ClassGroup, Student


class StudentInline(admin.TabularInline):
    model = Student
    fields = ("enrollment_number", "full_name", "user")
    extra = 0
    show_change_link = True

    def get_queryset(self, request: HttpRequest) -> QuerySet[Student]:
        return super().get_queryset(request).select_related("user")


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "is_active", "student_count")
    list_filter = ("is_active", "year")
    search_fields = ("name",)
    filter_horizontal = ("teachers",)
    inlines = [StudentInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[ClassGroup]:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("teachers")
            .annotate(annotated_student_count=Count("students"))
        )

    @admin.display(ordering="annotated_student_count", description="Alunos")
    def student_count(self, obj: ClassGroup) -> int:
        return obj.annotated_student_count


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("enrollment_number", "full_name", "class_group", "created_at")
    list_filter = ("class_group__year", "class_group")
    search_fields = ("enrollment_number", "full_name", "user__email")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("class_group",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Student]:
        return super().get_queryset(request).select_related("user", "class_group")
