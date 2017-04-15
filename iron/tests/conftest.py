import pytest

from rest_framework.test import APIClient


@pytest.fixture
def default_root(tmpdir, settings):
    settings.IRON_ROOT = str(tmpdir)
    return tmpdir


@pytest.fixture
def api_client():
    return APIClient(format='json')
