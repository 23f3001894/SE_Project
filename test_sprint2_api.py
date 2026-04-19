import pytest
from backend.app import create_app
from backend.models import db

@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

# ---------------- AUTH ----------------

def test_register_success(client):
    res = client.post('/api/auth/register', json={
        "name": "Sarwar",
        "email": "sarwar@test.com",
        "password": "1234",
        "role": "customer"
    })
    assert res.status_code == 201


def test_register_fail(client):
    res = client.post('/api/auth/register', json={
        "name": "Sarwar"
    })
    assert res.status_code == 400


def test_login_success(client):
    client.post('/api/auth/register', json={
        "name": "User",
        "email": "user@test.com",
        "password": "1234",
        "role": "customer"
    })

    res = client.post('/api/auth/login', json={
        "email": "user@test.com",
        "password": "1234"
    })
    assert res.status_code == 200


def test_login_fail(client):
    res = client.post('/api/auth/login', json={
        "email": "wrong@test.com",
        "password": "1234"
    })
    assert res.status_code == 401


# ---------------- PRODUCTS ----------------

def test_get_products(client):
    res = client.get('/api/products/')
    assert res.status_code == 200


def test_create_product_unauthorized(client):
    res = client.post('/api/products/', json={
        "name": "Rice",
        "quantity": 10,
        "price": 50
    })
    assert res.status_code in [401, 403]


# ---------------- CART ----------------

def test_add_to_cart_fail(client):
    res = client.post('/api/cart/add', json={
        "product_id": 1,
        "quantity": 2
    })
    assert res.status_code in [400, 401]


# ---------------- BOOKING ----------------

def test_booking_fail(client):
    res = client.post('/api/bookings/', json={
        "delivery_address_id": 1,
        "mode_of_payment": "COD"
    })
    assert res.status_code in [400, 401]