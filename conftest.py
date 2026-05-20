from django.conf import settings


def pytest_configure():
    settings.DATABASES["default"].setdefault("TEST", {})
