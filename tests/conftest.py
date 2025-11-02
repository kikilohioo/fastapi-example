import uuid
import pytest
from jose import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database import Base, get_db
from app.main import app
from app.config import settings
from app import schemas, models

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- FIXTURE: Base de datos de prueba ---
@pytest.fixture(scope='session')
def db_session():
    # Crear tablas antes de cada test
    print('')
    print('-------------------------------------------')
    print('creando session de base de datos de prueba')
    print('-------------------------------------------')
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        print('')
        print('----------------------------------------------')
        print('destruyendo session de base de datos de prueba')
        print('----------------------------------------------')
        db.close()
        Base.metadata.drop_all(bind=engine)


# --- FIXTURE: Cliente de test con DB temporal ---
@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# --- PAYLOAD DE USUARIO ---
@pytest.fixture
def create_user_payload_json():
    '''Proporciona un payload de usuario para los tests.'''

    return {
        'full_name': 'Test User',
        'email': f'testuser_{uuid.uuid4().hex[:8]}@example.com',
        'password': 'TestPassword123',
        'avatar_url': ''
    }


# --- PAYLOAD SCHEMA DE USUARIO ---
@pytest.fixture
def create_user_payload(create_user_payload_json):
    '''Proporciona un payload con schema de usuario para los tests.'''
    return schemas.UserCreate.model_validate(create_user_payload_json)


# --- CREAR USUARIO ---
@pytest.fixture
def test_user(client, create_user_payload_json, create_user_payload):
    '''Crea un usuario temporal para los tests.'''
    res = client.post('/users/', json=create_user_payload_json)
    assert res.status_code == 201, res.text

    user = schemas.UserResponse.model_validate(res.json())

    assert 'password' not in user, 'No debería devolverse la contraseña'
    # guardamos para el login posterior
    test_user = schemas.TestUser.model_validate(
        {**res.json(), 'password': create_user_payload.password})

    return test_user


# --- LOGIN Y TOKEN ---
@pytest.fixture
def test_user_token(client, test_user: schemas.TestUser):
    '''
    Crea un cliente temporal, inicia sesión con el usuario creado y 
    devuelve el token de autenticación.
    Solo se ejecuta una vez por sesión de pytest.
    '''
    # Login
    res = client.post('/auth/login', data={
        'username': test_user.email,
        'password': test_user.password
    })

    assert res.status_code == 200
    login_response = schemas.LoginResponse.model_validate(res.json())

    token = login_response.access_token

    payload = jwt.decode(token, settings.secret_key,
                         algorithms=[settings.algorithm])
    assert payload.get('user_id') == test_user.id

    return token


# --- CLIENTE AUTORIZADO ---
@pytest.fixture
def authorized_client(test_user_token: str):
    '''Cliente autenticado con token JWT en el header.'''
    app.dependency_overrides[get_db] = override_get_db
    auth_client = TestClient(app)
    auth_client.headers.update({
        'Authorization': f'Bearer {test_user_token}'
    })
    yield auth_client


@pytest.fixture
def test_posts(test_user, db_session):
    posts_data = [
        {
            'title': 'Titulo 1',
            'content': 'Content 1 con 10 caracteres minimo',
            'user_id': test_user.id
        },
        {
            'title': 'Titulo 2',
            'content': 'Content 2 con 10 caracteres minimo',
            'user_id': test_user.id
        },
        {
            'title': 'Titulo 3',
            'content': 'Content 3 con 10 caracteres minimo',
            'user_id': test_user.id
        }
    ]

    def create_post_model(post):
        return models.Post(**post)

    posts_map = map(create_post_model, posts_data)
    posts = list(posts_map)

    db_session.add_all(posts)
    db_session.commit()

    posts = db_session.query(models.Post).all()
    return posts


# --- FIXTURE TO TRY GET AN SPECIFIC POST ---
@pytest.fixture
def created_post(authorized_client):
    '''Crea un post temporal para los tests.'''
    payload = {
        'title': 'Post temporal',
        'content': 'Contenido temporal',
        'published': False
    }
    res = authorized_client.post('/posts/', json=payload)
    assert res.status_code == 201
    created_post = schemas.PostResponse.model_validate(res.json())
    return created_post
