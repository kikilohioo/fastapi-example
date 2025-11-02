from app import schemas


# --- CREATE A USER WITH VALID DATA ---
def test_create_user(test_user: schemas.TestUser, create_user_payload: schemas.UserCreate):
    '''
    Verifica que se pueda crear un usuario correctamente
    y que los datos devueltos coincidan con los esperados.
    '''
    assert test_user.email == create_user_payload.email
    assert test_user.full_name == create_user_payload.full_name
    assert test_user.role == create_user_payload.role
    assert test_user.id, 'Debe devolverse un ID'
    assert test_user.created_at, 'Debe incluir una fecha de creación'


# --- TRY CREATE A USER WITH DUPLICATE EMAIL ---
def test_create_user_duplicate_email(client, create_user_payload_json):
    '''
    Verifica que no se pueda crear un usuario 
    con un email ya registrado.
    '''
    # Crear el primer usuario
    client.post('/users/', json=create_user_payload_json)

    # Intentar crear otro con el mismo email
    res = client.post('/users/', json=create_user_payload_json)
    assert res.status_code == 409
    assert 'ya está registrado' in res.text


# --- GET USER BY ID ---
def test_get_user_valid(client, test_user):
    '''
    Verifica que se pueda obtener un usuario existente por su ID.
    '''
    res = client.get(f'/users/{test_user.id}')
    assert res.status_code == 200
    user = schemas.UserResponse.model_validate(res.json())
    assert user.id == test_user.id
    assert user.email == test_user.email
    assert user.full_name == test_user.full_name


# --- TRY GET A USER THAT DOES NOT EXIST ---
def test_get_user_not_found(client):
    '''
    Verifica que se maneje correctamente la solicitud
    de un usuario inexistente.
    '''
    res = client.get('/users/9999')
    assert res.status_code == 404
