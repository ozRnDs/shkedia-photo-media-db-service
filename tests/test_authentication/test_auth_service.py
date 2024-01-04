import pytest

from authentication.service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException

@pytest.fixture(scope="module")
def auth_service_fixture(jwt_key_location_fixture, mock_db_service):
    auth_service = AuthService(user_db_service=mock_db_service,
                                jwt_key_location=jwt_key_location_fixture)
    yield auth_service

def test_log_in_non_existing_user(auth_service_fixture):
    # SETUP
    test_form_data = OAuth2PasswordRequestForm(username="NonExisting",password="NonExisting")

    # RUN
    with pytest.raises(HTTPException) as err:
        token = auth_service_fixture.__log_in__(form_data=test_form_data)
        # ASSERT
    assert "Incorrect username or password" in err.value.detail
    