import json
from datetime import datetime, timedelta

import pytest

from backend.app import create_app
from backend.models import Address, Booking, BookingItem, Brand, Cart, CartItem, Offer, OfferNotification, Product, User, db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "JWT_SECRET_KEY": "test-jwt-secret-key-that-is-at-least-32-bytes",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {"Content-Type": "application/json"}


def _login_and_get_token(client, auth_headers, email, password):
    response = client.post(
        "/api/auth/login",
        data=json.dumps({"email": email, "password": password}),
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = json.loads(response.data)
    return payload["access_token"]


@pytest.fixture
def admin_user(app, client, auth_headers):
    with app.app_context():
        user = User(name="Admin User", email="admin@agriflow.com", role="admin")
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    token = _login_and_get_token(client, auth_headers, "admin@agriflow.com", "admin123")
    return {"Authorization": f"Bearer {token}", "X-User-ID": str(user_id)}


@pytest.fixture
def customer_user(app, client, auth_headers):
    with app.app_context():
        user = User(name="Test Customer", email="customer@agriflow.com", role="customer")
        user.set_password("customer123")
        db.session.add(user)
        db.session.commit()
        db.session.add(Cart(user_id=user.id))
        db.session.commit()
        user_id = user.id

    token = _login_and_get_token(client, auth_headers, "customer@agriflow.com", "customer123")
    return {"Authorization": f"Bearer {token}", "X-User-ID": str(user_id)}


@pytest.fixture
def second_customer(app, client, auth_headers):
    with app.app_context():
        user = User(name="Second Customer", email="customer2@agriflow.com", role="customer")
        user.set_password("customer123")
        db.session.add(user)
        db.session.commit()
        db.session.add(Cart(user_id=user.id))
        db.session.commit()
        user_id = user.id

    token = _login_and_get_token(client, auth_headers, "customer2@agriflow.com", "customer123")
    return {"Authorization": f"Bearer {token}", "X-User-ID": str(user_id)}


@pytest.fixture
def sample_product(app, admin_user):
    with app.app_context():
        brand = Brand.query.filter_by(name="Harvest Hill").first()
        if not brand:
            brand = Brand(name="Harvest Hill")
            db.session.add(brand)
            db.session.flush()

        product = Product(
            name="Organic Tomatoes",
            description="Fresh organic tomatoes",
            quantity=100,
            price=50.0,
            expiry_date=datetime.utcnow() + timedelta(days=30),
            brand_id=brand.id,
            admin_id=int(admin_user["X-User-ID"]),
            image_path="/static/images/product-placeholder.svg",
        )
        db.session.add(product)
        db.session.commit()
        return product.id


@pytest.fixture
def second_admin_with_product(app):
    with app.app_context():
        admin = User(name="Second Admin", email="other-admin@agriflow.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()

        brand = Brand(name="Other Brand")
        db.session.add(brand)
        db.session.flush()

        product = Product(
            name="Other Seller Product",
            description="Belongs to other admin",
            quantity=25,
            price=60.0,
            brand_id=brand.id,
            admin_id=admin.id,
        )
        db.session.add(product)
        db.session.commit()
        return {"admin_id": admin.id, "product_id": product.id}


@pytest.fixture
def customer_address(app, customer_user):
    with app.app_context():
        address = Address(
            user_id=int(customer_user["X-User-ID"]),
            address_line_1="123 Main Street",
            city="Mumbai",
            state="Maharashtra",
            pin_code="400001",
        )
        db.session.add(address)
        db.session.commit()
        return address.id


@pytest.fixture
def active_offer(app):
    with app.app_context():
        offer = Offer(
            title="Festival Offer",
            description="Limited-time deal",
            discount_type="percentage",
            discount_value=15,
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=7),
            is_active=True,
        )
        db.session.add(offer)
        db.session.commit()
        return offer.id


def seed_booking_for_customer(app, customer_id, product_id, quantity=2, status="pending"):
    with app.app_context():
        address = Address(
            user_id=customer_id,
            address_line_1="456 Delivery Road",
            city="Pune",
            state="Maharashtra",
            pin_code="411001",
        )
        db.session.add(address)
        db.session.flush()

        product = db.session.get(Product, product_id)
        booking = Booking(
            user_id=customer_id,
            total_price=product.price * quantity,
            delivery_address_id=address.id,
            mode_of_payment="Cash",
            status=status,
        )
        db.session.add(booking)
        db.session.flush()

        db.session.add(
            BookingItem(
                booking_id=booking.id,
                product_id=product_id,
                quantity=quantity,
                price_at_purchase=product.price,
            )
        )
        db.session.commit()
        return booking.id


def seed_offer_notification(app, offer_id, user_id):
    with app.app_context():
        record = OfferNotification(offer_id=offer_id, user_id=user_id)
        db.session.add(record)
        db.session.commit()
        return record.id
