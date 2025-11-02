import pytest
from app import schemas

# --- TESTS DE AUTENTICACIÓN WITH VALID CREDENTIALS ---


def test_login_valid(client, test_user: schemas.TestUser):
    '''
    Verifica que se pueda iniciar sesión con credenciales válidas.
    '''
    res = client.post('/auth/login/', data={
        'username': test_user.email,
        'password': test_user.password
    })
    assert res.status_code == 200
    body = res.json()
    login_response = schemas.LoginResponse.model_validate(body)
    assert login_response.user.email == test_user.email


# --- TESTS DE AUTENTICACIÓN WITH INVALID EMAIL ---
@pytest.mark.parametrize('wrong_email,  expected_status_code', [
    ('noexiste@example', 403),
    ('invalidemail', 403),
    (None, 422),
])
def test_login_invalid_email(client, wrong_email, expected_status_code):
    '''
    Verifica que no se pueda iniciar sesión con un email inválido.
    '''
    if not wrong_email:
        res = client.post('/auth/login/', data={
            'password': 'whatever'
        })
        assert res.status_code == expected_status_code
    else:
        res = client.post('/auth/login/', data={
            'username': wrong_email,
            'password': 'whatever'
        })
        assert res.status_code == expected_status_code
        assert 'Credenciales inválidas' in res.text


# --- TESTS DE AUTENTICACIÓN WITH INVALID PASSWORD ---
@pytest.mark.parametrize('wrong_password, expected_status_code', [
    ('somepassword1', 403),
    ('somepassword2', 403),
    (None, 422),
])
def test_login_invalid_password(client, test_user: schemas.TestUser, wrong_password, expected_status_code):
    '''
    Verifica que no se pueda iniciar sesión con una contraseña inválida.
    '''
    if not wrong_password:
        res = client.post('/auth/login/', data={
            'username': test_user.email
        })
        assert res.status_code == expected_status_code
    else:
        res = client.post('/auth/login/', data={
            'username': test_user.email,
            'password': wrong_password
        })
        assert res.status_code == expected_status_code
