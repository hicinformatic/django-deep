import pytest

@pytest.mark.django_db
def test_model_creation():
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()
    instance = UserModel.objects.create_user(
        username="testuser",
        password="password123",
        email="test@test.com"
    )
    assert instance.username == "testuser"
