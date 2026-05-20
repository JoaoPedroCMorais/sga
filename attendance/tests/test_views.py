import pytest
from django.urls import reverse

from academic.models import ClassGroup, Student
from users.models import User


@pytest.fixture
def class_group(db):
    return ClassGroup.objects.create(name="Extensivo Manhã", year=2026)


@pytest.fixture
def monitor(db):
    return User.objects.create_user(
        email="monitor@sga.test",
        password="pass",
        role=User.Role.MONITOR,
    )


@pytest.fixture
def coordenador(db):
    return User.objects.create_user(
        email="coord@sga.test",
        password="pass",
        role=User.Role.COORDENADOR,
    )


@pytest.fixture
def aluno_user(db):
    return User.objects.create_user(
        email="aluno@sga.test",
        password="pass",
        role=User.Role.ALUNO,
    )


@pytest.fixture
def professor_user(db):
    return User.objects.create_user(
        email="prof@sga.test",
        password="pass",
        role=User.Role.PROFESSOR,
    )


@pytest.fixture
def students(db, aluno_user, class_group):
    return [
        Student.objects.create(
            user=aluno_user,
            enrollment_number="2026001",
            full_name="Maria Souza",
            class_group=class_group,
        )
    ]


def get_url(class_group_id: int) -> str:
    return reverse(
        "attendance:take_attendance", kwargs={"class_group_id": class_group_id}
    )


@pytest.mark.django_db
class TestTakeAttendanceViewRBAC:
    def test_monitor_gets_200(self, client, monitor, class_group, students):
        client.force_login(monitor)
        response = client.get(get_url(class_group.pk))
        assert response.status_code == 200

    def test_coordenador_gets_200(self, client, coordenador, class_group, students):
        client.force_login(coordenador)
        response = client.get(get_url(class_group.pk))
        assert response.status_code == 200

    def test_aluno_gets_403(self, client, aluno_user, class_group):
        client.force_login(aluno_user)
        response = client.get(get_url(class_group.pk))
        assert response.status_code == 403

    def test_professor_gets_403(self, client, professor_user, class_group):
        client.force_login(professor_user)
        response = client.get(get_url(class_group.pk))
        assert response.status_code == 403

    def test_unauthenticated_redirects_to_login(self, client, class_group):
        response = client.get(get_url(class_group.pk))
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
class TestTakeAttendanceViewQueryset:
    def test_lists_only_students_of_given_class(
        self, client, monitor, class_group, students
    ):
        client.force_login(monitor)
        response = client.get(get_url(class_group.pk))
        assert list(response.context["students"]) == students

    def test_context_contains_class_group(self, client, monitor, class_group, students):
        client.force_login(monitor)
        response = client.get(get_url(class_group.pk))
        assert response.context["class_group"] == class_group

    def test_context_contains_active_class_groups(
        self, client, monitor, class_group, students
    ):
        client.force_login(monitor)
        response = client.get(get_url(class_group.pk))
        assert class_group in response.context["class_groups"]

    def test_empty_queryset_for_nonexistent_class(self, client, monitor):
        client.force_login(monitor)
        response = client.get(get_url(99999))
        assert response.status_code == 200
        assert len(response.context["students"]) == 0
