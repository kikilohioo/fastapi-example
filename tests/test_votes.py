import pytest


@pytest.fixture
def voted_post(authorized_client, created_post):
    """Crea un post ya votado."""
    res = authorized_client.post('/votes/', json={
        'post_id': created_post.id,
        'dir': 1
    })
    assert res.status_code == 201
    return created_post


@pytest.fixture
def non_existing_post_id():
    """Devuelve un ID seguro inexistente."""
    return 999999999


# --- VOTE / UNVOTE A POST ---
@pytest.mark.parametrize('dir, expected_status', [
    (1, 201),   # votar
    (0, 204),   # desvotar
])
def test_vote_post(authorized_client, created_post, dir, expected_status):
    """
    El usuario puede votar y desvotar un post correctamente.
    """
    # Si vamos a desvotar, primero votamos
    if dir == 0:
        authorized_client.post(
            '/votes/', json={'post_id': created_post.id, 'dir': 1})

    res = authorized_client.post('/votes/', json={
        'post_id': created_post.id,
        'dir': dir
    })

    assert res.status_code == expected_status
    if dir == 1:
        assert res.json().get('message') == 'Vote recorded successfully'


# --- VOTE INVALID CASES ---
@pytest.mark.parametrize('dir', [1, 0])
def test_vote_non_existing_post(authorized_client, non_existing_post_id, dir):
    """
    No se puede votar un post que no existe.
    """
    res = authorized_client.post('/votes/', json={
        'post_id': non_existing_post_id,
        'dir': dir
    })
    assert res.status_code == 404


def test_vote_already_voted_post(authorized_client, voted_post):
    """
    No se puede volver a votar un post ya votado.
    """
    res = authorized_client.post('/votes/', json={
        'post_id': voted_post.id,
        'dir': 1
    })
    assert res.status_code == 409


# --- UNAUTHORIZED USER ---
def test_unauthorized_vote_post(client, created_post):
    """
    Un usuario no autenticado no puede votar.
    """
    res = client.post('/votes/', json={
        'post_id': created_post.id,
        'dir': 1
    })
    assert res.status_code == 401
