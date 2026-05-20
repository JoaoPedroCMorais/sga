import pytest
from django.db import IntegrityError
from django.utils import timezone

from academic.models import ClassGroup, Student
from attendance.models import AbsenceJustification, AttendanceRecord
from users.models import User


@pytest.fixture
def monitor(db):
    return User.objects.create_user(
        email="monitor@sga.test",
        password="pass",
        role=User.Role.MONITOR,
    )


@pytest.fixture
def class_group(db):
    return ClassGroup.objects.create(name="Extensivo Manhã", year=2026)


@pytest.fixture
def aluno_user(db):
    return User.objects.create_user(
        email="aluno@sga.test",
        password="pass",
        role=User.Role.ALUNO,
    )


@pytest.fixture
def student(db, aluno_user, class_group):
    return Student.objects.create(
        user=aluno_user,
        enrollment_number="2026001",
        full_name="João Silva",
        class_group=class_group,
    )


@pytest.mark.django_db
class TestAttendanceRecord:
    def test_create(self, student, monitor):
        record = AttendanceRecord.objects.create(
            student=student,
            date=timezone.now().date(),
            status=AttendanceRecord.Status.PRESENT,
            observer=monitor,
        )
        assert record.pk is not None
        assert record.status == AttendanceRecord.Status.PRESENT

    def test_default_status_is_absent(self, student, monitor):
        record = AttendanceRecord.objects.create(
            student=student,
            date=timezone.now().date(),
            observer=monitor,
        )
        assert record.status == AttendanceRecord.Status.ABSENT

    def test_str_contains_student_and_date(self, student, monitor):
        today = timezone.now().date()
        record = AttendanceRecord(
            student=student,
            date=today,
            status=AttendanceRecord.Status.ABSENT,
            observer=monitor,
        )
        assert str(student) in str(record)
        assert str(today) in str(record)

    def test_unique_per_student_per_day(self, student, monitor):
        today = timezone.now().date()
        AttendanceRecord.objects.create(
            student=student,
            date=today,
            status=AttendanceRecord.Status.PRESENT,
            observer=monitor,
        )
        with pytest.raises(IntegrityError):
            AttendanceRecord.objects.create(
                student=student,
                date=today,
                status=AttendanceRecord.Status.ABSENT,
                observer=monitor,
            )

    def test_timestamps_are_set(self, student, monitor):
        record = AttendanceRecord.objects.create(
            student=student,
            date=timezone.now().date(),
            status=AttendanceRecord.Status.PRESENT,
            observer=monitor,
        )
        assert record.created_at is not None
        assert record.updated_at is not None


@pytest.mark.django_db
class TestAbsenceJustification:
    def test_create(self, student):
        justification = AbsenceJustification.objects.create(
            student=student,
            date=timezone.now().date(),
            reason="Atestado médico",
        )
        assert justification.pk is not None
        assert justification.status == AbsenceJustification.Status.PENDING

    def test_str_contains_student_and_date(self, student):
        today = timezone.now().date()
        j = AbsenceJustification(
            student=student,
            date=today,
            reason="Consulta",
            status=AbsenceJustification.Status.PENDING,
        )
        assert str(student) in str(j)
        assert str(today) in str(j)

    def test_reviewer_is_optional(self, student):
        j = AbsenceJustification.objects.create(
            student=student,
            date=timezone.now().date(),
            reason="Viagem",
        )
        assert j.reviewer is None

    def test_file_url_is_optional(self, student):
        j = AbsenceJustification.objects.create(
            student=student,
            date=timezone.now().date(),
            reason="Motivo qualquer",
        )
        assert j.file_url == ""

    def test_timestamps_are_set(self, student):
        j = AbsenceJustification.objects.create(
            student=student,
            date=timezone.now().date(),
            reason="Teste",
        )
        assert j.created_at is not None
        assert j.updated_at is not None
