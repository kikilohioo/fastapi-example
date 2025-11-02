import pytest
from app import schemas


# --- GET ALL POSTS FOR AN AUTHORIZED USER ---
def test_get_all_posts(authorized_client, test_posts):
    '''
    Intentamos obtener todos los posts
    '''
    res = authorized_client.get('/posts/')

    def validate_schema(post):
        assert schemas.PostOut.model_validate(post)

    map(validate_schema, res.json())

    assert res.status_code == 200
    assert len(res.json()) == len(test_posts)


# --- TRY GET ALL POSTS FOR AN UNAUTHORIZED USER ---
def test_get_unauthorized_all_post(client):
    '''
    Intentamos obtener todos los posts sin estar autorizado
    '''
    res = client.get('/posts/')
    assert res.status_code == 401


# --- TRY GET ALL POSTS FOR AN UNAUTHORIZED USER ---
def test_get_unauthorized_post(client, test_posts):
    '''
    Intentamos obtener un post sin estar autorizado
    '''
    res = client.get(f'/posts/{test_posts[0].id}')
    assert res.status_code == 401


# --- CREATE A POST WITH ALL THE EXPECTED FIELDS ---
@pytest.mark.parametrize('title, content, published', [
    ('Mi primer post', 'Contenido de prueba del post 1', True),
    ('Mi segundo post', 'Contenido de prueba del post 2', False),
    ('Mi tercer post', 'Contenido de prueba del post 3', None),
])
def test_create_post_valid_fields(authorized_client, title, content, published):
    '''
    Verifica que un usuario autenticado pueda crear un post correctamente.
    Con todos los campos esperados.
    '''
    res = authorized_client.post('/posts/', json={
        'title': title,
        'content': content,
        'published': published
    })
    assert res.status_code == 201, res.text

    new_post = schemas.PostResponse.model_validate(res.json())

    is_published = published if published is not None else True
    assert new_post.title == title
    assert new_post.content == content
    assert new_post.published == is_published


# --- TRY CREATE A POST WITHOUT ALL THE EXPECTED FIELDS ---
@pytest.mark.parametrize(
    'payload, expected_status',
    [
        ({'title': None, 'content': 'contenido',
         'published': True}, 422),  # title None
        ({'title': 'titulo', 'content': None,
         'published': True}, 422),     # content None
    ]
)
def test_create_post_invalid_fields(authorized_client, payload, expected_status):
    '''
    Verifica que un usuario autenticado pueda crear un post correctamente.
    Sin todos los campos esperados.
    '''
    res = authorized_client.post('/posts/', json=payload)
    assert res.status_code == expected_status


# --- TRY CREATE A POST WITHOUT AUTHENTICATION ---
def test_create_post_unauthorized(client):
    '''
    Verifica que no se pueda crear un post sin autenticación.
    '''
    res = client.post('/posts/', json={
        'title': 'Post sin token',
        'content': 'No debería crearse'
    })
    assert res.status_code == 401


# --- GET ALL POST FOR AN AUTHENTICATED USER ---
def test_get_posts(authorized_client):
    '''
    Verifica que el usuario pueda listar sus posts.
    '''
    res = authorized_client.get('/posts/')
    assert res.status_code == 200
    posts = res.json()
    assert isinstance(posts, list)


# --- TRY GET A POST THAT DOES NOT EXIST ---
def test_get_post_not_found(authorized_client):
    '''
    Verifica que se maneje correctamente la solicitud
    de un post que no existe.
    '''
    res = authorized_client.get('/posts/9999')
    assert res.status_code == 404


# --- GET POST BY ID ---
def test_get_post_by_id(authorized_client, created_post: schemas.PostResponse):
    '''
    Verifica que se pueda obtener un post por su ID.
    '''
    post_id = created_post.id
    res = authorized_client.get(f'/posts/{post_id}/')
    assert res.status_code == 200

    fetched_post = res.json()
    post_out = schemas.PostOut.model_validate(fetched_post)

    assert post_out.Post.id == post_id
    assert post_out.Post.title == created_post.title
    assert post_out.Post.content == created_post.content
    assert post_out.Post.published == created_post.published


# --- DELETE POST ---
def test_delete_post(authorized_client, created_post: schemas.PostResponse):
    '''
    Verifica que el usuario pueda eliminar su propio post.
    '''
    post_id = created_post.id

    res = authorized_client.delete(f'/posts/{post_id}/')
    assert res.status_code in (200, 204)

    # Asegurarse de que ya no existe
    res_check = authorized_client.get(f'/posts/{post_id}/')
    assert res_check.status_code == 404


# --- UPDATE A POST ---
@pytest.mark.parametrize('title, content, published', [
    ('Mi primer post actualizado', 'Contenido actualizado de  prueba del post 1', False),
    ('Mi segundo post actualizado', 'Contenido actualizado de prueba del post 2', True),
    ('Mi tercer post actualizado', 'Contenido actualizado de prueba del post 3', None),
])
def test_update_post(authorized_client, created_post, title, content, published):
    res = authorized_client.put(f'/posts/{created_post.id}/', json={
        'title': title,
        'content': content,
        'published': published
    })

    updated_post = schemas.PostResponse.model_validate(res.json())

    is_published = published if published is not None else created_post.published

    assert res.status_code == 200
    assert updated_post.title == title
    assert updated_post.content == content
    assert updated_post.published == is_published


# --- TRY UNAUTHORIZED UPDATE POST ---
def test_update_unauthorized_post(client, created_post):
    res = client.put(f'/posts/{created_post.id}', json={
        'title': 'test title',
        'content': 'test content with more than 10 chars',
        'published': False
    })
    assert res.status_code == 401
