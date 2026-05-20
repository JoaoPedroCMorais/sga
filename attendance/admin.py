from django.contrib import admin

from .models import AbsenceJustification, AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "get_class_group", "date", "status", "observer")
    list_filter = ("status", "date", "student__class_group")
    search_fields = (
        "student__full_name",
        "student__enrollment_number",
        "observer__email",
    )
    date_hierarchy = "date"
    raw_id_fields = ("student", "observer")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("student__class_group", "observer")
        )

    @admin.display(description="Turma", ordering="student__class_group__name")
    def get_class_group(self, obj: AttendanceRecord) -> str:
        return obj.student.class_group.name


@admin.register(AbsenceJustification)
class AbsenceJustificationAdmin(admin.ModelAdmin):
    list_display = ("student", "get_class_group", "date", "status", "reviewer")
    list_filter = ("status", "date", "student__class_group")
    search_fields = ("student__full_name", "student__enrollment_number")
    date_hierarchy = "date"
    raw_id_fields = ("student", "reviewer")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("student__class_group", "reviewer")
        )

    @admin.display(description="Turma", ordering="student__class_group__name")
    def get_class_group(self, obj: AbsenceJustification) -> str:
        return obj.student.class_group.name
