import pytest
# Импортируем rest_framework только ПОСЛЕ того, как pytest настроит окружение
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username='test123test',
        password='password123password',
        email='test123@gmail.com',)


@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.mark.django_db
def test_cart(auth_client):
    response = auth_client.get('/api/v1/cart/')
    assert response.status_code == 200