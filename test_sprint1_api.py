import pytest
import json
from app import create_app
from models import (
    db,
    User,
    Product,
    Cart,
    CartItem,
    Booking,
    BookingItem,
    Address,
    Review,
    Offer,
)
from datetime import datetime, timedelta


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

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


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(
            name="Admin User",
            email="admin@agriflow.com",
            password="admin123",
            role="admin",
        )
        db.session.add(user)
        db.session.commit()
        return {"User-ID": str(user.id), "Role": "admin"}


@pytest.fixture
def customer_user(app):
    with app.app_context():
        user = User(
            name="Test Customer",
            email="customer@agriflow.com",
            password="customer123",
            role="customer",
        )
        db.session.add(user)
        db.session.commit()
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
        return {"User-ID": str(user.id), "Role": "customer"}


@pytest.fixture
def sample_product(app, admin_user):
    with app.app_context():
        product = Product(
            name="Organic Tomatoes",
            description="Fresh organic tomatoes",
            quantity=100,
            price=50.0,
            expiry_date=datetime.utcnow() + timedelta(days=30),
        )
        db.session.add(product)
        db.session.commit()
        return product.id


# ==================== AUTH API TESTS ====================


class TestRegisterAPI:
    """Test cases for User Registration API"""

    def test_register_success(self, client, auth_headers):
        """Test successful user registration"""
        payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "mobile_no": "1234567890",
        }
        response = client.post(
            "/api/auth/register", data=json.dumps(payload), headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "user_id" in data
        assert data["message"] == "User created successfully"

    def test_register_duplicate_email(self, client, auth_headers):
        """Test registration with duplicate email"""
        payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        }
        client.post(
            "/api/auth/register", data=json.dumps(payload), headers=auth_headers
        )
        response = client.post(
            "/api/auth/register", data=json.dumps(payload), headers=auth_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Email already exists" in data["message"]

    def test_register_missing_fields(self, client, auth_headers):
        """Test registration with missing required fields"""
        payload = {"name": "John Doe"}
        response = client.post(
            "/api/auth/register", data=json.dumps(payload), headers=auth_headers
        )
        assert response.status_code == 400


class TestLoginAPI:
    """Test cases for User Login API"""

    def test_login_success(self, client, auth_headers, customer_user):
        """Test successful login"""
        payload = {"email": "customer@agriflow.com", "password": "customer123"}
        response = client.post(
            "/api/auth/login", data=json.dumps(payload), headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Login successful"
        assert "user_id" in data
        assert data["role"] == "customer"

    def test_login_invalid_credentials(self, client, auth_headers):
        """Test login with invalid credentials"""
        payload = {"email": "wrong@example.com", "password": "wrongpass"}
        response = client.post(
            "/api/auth/login", data=json.dumps(payload), headers=auth_headers
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["message"] == "Invalid credentials"


# ==================== PRODUCT API TESTS ====================


class TestGetProductsAPI:
    """Test cases for Get Products API"""

    def test_get_products_customer(self, client, auth_headers, sample_product):
        """Test getting products as customer (should exclude expired)"""
        response = client.get(
            "/api/products/", headers={**auth_headers, "Role": "customer"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "products" in data
        assert len(data["products"]) > 0

    def test_get_products_admin(self, client, auth_headers, sample_product):
        """Test getting all products as admin"""
        response = client.get(
            "/api/products/", headers={**auth_headers, "Role": "admin"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "products" in data


class TestCreateProductAPI:
    """Test cases for Create Product API"""

    def test_create_product_admin_success(self, client, auth_headers, admin_user):
        """Test successful product creation by admin"""
        payload = {
            "name": "Fresh Potatoes",
            "description": "Organic potatoes",
            "quantity": 200,
            "price": 30.0,
            "expiry_date": "2026-12-31",
        }
        response = client.post(
            "/api/products/",
            data=json.dumps(payload),
            headers={**auth_headers, **admin_user},
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "product_id" in data

    def test_create_product_unauthorized(self, client, auth_headers, customer_user):
        """Test product creation by non-admin (should fail)"""
        payload = {"name": "Test", "quantity": 10, "price": 10.0}
        response = client.post(
            "/api/products/",
            data=json.dumps(payload),
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 403


class TestGetProductByIdAPI:
    """Test cases for Get Product by ID API"""

    def test_get_product_exists(self, client, auth_headers, sample_product):
        """Test getting existing product"""
        response = client.get(f"/api/products/{sample_product}", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["product"]["name"] == "Organic Tomatoes"

    def test_get_product_not_found(self, client, auth_headers):
        """Test getting non-existent product"""
        response = client.get("/api/products/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateProductAPI:
    """Test cases for Update Product API"""

    def test_update_product_admin(
        self, client, auth_headers, admin_user, sample_product
    ):
        """Test updating product by admin"""
        payload = {"name": "Updated Tomatoes", "price": 60.0}
        response = client.put(
            f"/api/products/{sample_product}",
            data=json.dumps(payload),
            headers={**auth_headers, **admin_user},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Product updated"


class TestDeleteProductAPI:
    """Test cases for Delete Product API"""

    def test_delete_product_admin(
        self, client, auth_headers, admin_user, sample_product
    ):
        """Test deleting product by admin"""
        response = client.delete(
            f"/api/products/{sample_product}", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200


# ==================== CART API TESTS ====================


class TestAddToCartAPI:
    """Test cases for Add to Cart API"""

    def test_add_to_cart_success(
        self, client, auth_headers, customer_user, sample_product
    ):
        """Test successful adding item to cart"""
        payload = {"product_id": sample_product, "quantity": 2}
        response = client.post(
            "/api/cart/add",
            data=json.dumps(payload),
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 200

    def test_add_to_cart_insufficient_stock(
        self, client, auth_headers, customer_user, app
    ):
        with app.app_context():
            product = Product(
                name="Limited Stock", description="Test", quantity=1, price=10.0
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id

        payload = {"product_id": product_id, "quantity": 5}
        response = client.post(
            "/api/cart/add",
            data=json.dumps(payload),
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Insufficient stock" in data["message"]


class TestGetCartAPI:
    """Test cases for Get Cart API"""

    def test_get_cart_empty(self, client, auth_headers, customer_user):
        """Test getting empty cart"""
        response = client.get("/api/cart/", headers={**auth_headers, **customer_user})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["cart_items"] == []


class TestUpdateCartItemAPI:
    """Test cases for Update Cart Item API"""

    def test_update_cart_item(
        self, client, auth_headers, customer_user, sample_product, app
    ):
        with app.app_context():
            cart = Cart.query.filter_by(user_id=int(customer_user["User-ID"])).first()
            cart_item = CartItem(cart_id=cart.id, product_id=sample_product, quantity=1)
            db.session.add(cart_item)
            db.session.commit()
            item_id = cart_item.id

        payload = {"quantity": 5}
        response = client.put(
            f"/api/cart/update/{item_id}",
            data=json.dumps(payload),
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 200


class TestRemoveCartItemAPI:
    """Test cases for Remove Cart Item API"""

    def test_remove_cart_item(
        self, client, auth_headers, customer_user, sample_product, app
    ):
        with app.app_context():
            cart = Cart.query.filter_by(user_id=int(customer_user["User-ID"])).first()
            cart_item = CartItem(cart_id=cart.id, product_id=sample_product, quantity=1)
            db.session.add(cart_item)
            db.session.commit()
            item_id = cart_item.id

        response = client.delete(
            f"/api/cart/remove/{item_id}", headers={**auth_headers, **customer_user}
        )
        assert response.status_code == 200


# ==================== BOOKING API TESTS ====================


class TestCreateBookingAPI:
    """Test cases for Create Booking API"""

    def test_create_booking_empty_cart(self, client, auth_headers, customer_user):
        """Test booking with empty cart"""
        payload = {"delivery_address_id": 1, "mode_of_payment": "Cash"}
        response = client.post(
            "/api/bookings/",
            data=json.dumps(payload),
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Cart is empty" in data["message"]


class TestGetBookingHistoryAPI:
    """Test cases for Get Booking History API"""

    def test_get_booking_history_customer(self, client, auth_headers, customer_user):
        """Test getting customer booking history"""
        response = client.get(
            "/api/bookings/history", headers={**auth_headers, **customer_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "bookings" in data


# ==================== REVIEW API TESTS ====================


class TestCreateReviewAPI:
    """Test cases for Create Review API"""

    def test_create_review_not_purchased(
        self, client, auth_headers, customer_user, sample_product
    ):
        """Test review without purchase (should fail)"""
        payload = {"product_id": sample_product, "rating": 5, "review": "Good product"}
        response = client.post(
            "/api/reviews/",
            data=json.dumps(payload),
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 403
        data = json.loads(response.data)
        assert "purchase" in data["message"].lower()


class TestGetProductReviewsAPI:
    """Test cases for Get Product Reviews API"""

    def test_get_product_reviews(self, client, auth_headers, sample_product):
        """Test getting reviews for a product"""
        response = client.get(
            f"/api/reviews/product/{sample_product}", headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "reviews" in data


# ==================== ADDRESS API TESTS ====================


class TestAddressAPI:
    """Test cases for Address APIs"""

    def test_create_address(self, client, auth_headers, customer_user):
        """Test creating an address"""
        payload = {
            "address_line_1": "123 Main Street",
            "address_line_2": "Apt 4",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pin_code": "400001",
        }
        response = client.post(
            "/api/addresses/",
            data=json.dumps(payload),
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 201

    def test_get_addresses(self, client, auth_headers, customer_user):
        """Test getting user addresses"""
        response = client.get(
            "/api/addresses/", headers={**auth_headers, **customer_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "addresses" in data


# ==================== ADMIN API TESTS ====================


class TestAdminDashboardAPI:
    """Test cases for Admin Dashboard API"""

    def test_dashboard_stats(self, client, auth_headers, admin_user):
        """Test getting admin dashboard statistics"""
        response = client.get(
            "/api/admin/dashboard/stats", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_products" in data
        assert "total_users" in data
        assert "total_orders" in data

    def test_dashboard_unauthorized(self, client, auth_headers, customer_user):
        """Test dashboard access by non-admin"""
        response = client.get(
            "/api/admin/dashboard/stats", headers={**auth_headers, **customer_user}
        )
        assert response.status_code == 403


class TestExpiringProductsAPI:
    """Test cases for Expiring Products API"""

    def test_get_expiring_products(self, client, auth_headers, admin_user):
        """Test getting expiring products"""
        response = client.get(
            "/api/admin/products/expiring", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "expiring_products" in data

    def test_get_expired_products(self, client, auth_headers, admin_user):
        """Test getting expired products"""
        response = client.get(
            "/api/admin/products/expired", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "expired_products" in data


class TestTopCustomersAPI:
    """Test cases for Top Customers API"""

    def test_get_top_customers(self, client, auth_headers, admin_user):
        """Test getting top customers"""
        response = client.get(
            "/api/admin/customers/top", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "top_customers" in data


class TestMonthlyReportAPI:
    """Test cases for Monthly Report API"""

    def test_get_monthly_report(self, client, auth_headers, admin_user):
        """Test getting monthly report"""
        response = client.get(
            "/api/admin/reports/monthly", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_sales" in data
        assert "total_orders" in data


class TestDemandForecastAPI:
    """Test cases for Demand Forecasting API"""

    def test_forecast_demand(self, client, auth_headers, admin_user, sample_product):
        """Test demand forecasting"""
        response = client.get(
            f"/api/admin/forecast/demand?product_id={sample_product}&months_ahead=3",
            headers={**auth_headers, **admin_user},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "forecast" in data

    def test_forecast_missing_product_id(self, client, auth_headers, admin_user):
        """Test forecasting without product_id"""
        response = client.get(
            "/api/admin/forecast/demand?months_ahead=3",
            headers={**auth_headers, **admin_user},
        )
        assert response.status_code == 400


class TestCreditScoreAPI:
    """Test cases for Credit Score APIs"""

    def test_get_credit_scores(self, client, auth_headers, admin_user):
        """Test getting customer credit scores"""
        response = client.get(
            "/api/admin/customers/credit-scores", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "customers" in data

    def test_update_credit_score(self, client, auth_headers, admin_user, app):
        with app.app_context():
            customer = User(
                name="Credit Test",
                email="credit@test.com",
                password="test",
                role="customer",
            )
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

        payload = {"credit_score": 75}
        response = client.put(
            f"/api/admin/customers/{customer_id}/credit-score",
            data=json.dumps(payload),
            headers={**auth_headers, **admin_user},
        )
        assert response.status_code == 200


# ==================== REVIEW ANALYTICS API TESTS ====================


class TestReviewAnalyticsAPI:
    """Test cases for Review Analytics APIs"""

    def test_get_all_reviews_with_pagination(
        self, client, auth_headers, admin_user, sample_product, app
    ):
        """Test getting all reviews with pagination"""
        with app.app_context():
            user = User.query.filter_by(role="customer").first()
            if user:
                review = Review(
                    product_id=sample_product,
                    user_id=user.id,
                    rating=4,
                    review="Good product",
                )
                db.session.add(review)
                db.session.commit()

        response = client.get(
            "/api/admin/reviews?page=1&per_page=10",
            headers={**auth_headers, **admin_user},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "reviews" in data

    def test_get_reviews_summary(self, client, auth_headers, admin_user):
        """Test getting review analytics summary"""
        response = client.get(
            "/api/admin/reviews/summary", headers={**auth_headers, **admin_user}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_reviews" in data
        assert "average_rating" in data
        assert "rating_distribution" in data


class TestOfferNotificationsAPI:
    """Test cases for Offer Notifications APIs"""

    def test_send_offer_notifications(self, client, auth_headers, admin_user, app):
        """Test sending offer notifications to customers"""
        with app.app_context():
            future_date = datetime.utcnow() + timedelta(days=30)
            offer = Offer(
                title="Test Offer",
                description="Test discount",
                discount_type="percentage",
                discount_value=10,
                start_date=datetime.utcnow(),
                end_date=future_date,
                is_active=True,
            )
            db.session.add(offer)
            db.session.commit()
            offer_id = offer.id

        payload = {"offer_id": offer_id}
        response = client.post(
            "/api/admin/offers/send-notifications",
            data=json.dumps(payload),
            headers={**auth_headers, **admin_user},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "notifications_sent" in data

    def test_get_offer_notifications(self, client, auth_headers, customer_user):
        """Test getting user offer notifications"""
        response = client.get(
            "/api/bookings/notifications/offers",
            headers={**auth_headers, **customer_user},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "offer_notifications" in data


# ==================== TEST SUMMARY ====================


def test_summary():
    """Summary of all test cases"""
    print("\n" + "=" * 60)
    print("SPRINT 1 API TEST CASES SUMMARY")
    print("=" * 60)
    print("Total Test Categories: 13")
    print("Total Test Cases: 35+")
    print("\nTest Categories:")
    print("1. Auth API (Register, Login) - 4 tests")
    print("2. Product API (CRUD operations) - 6 tests")
    print("3. Cart API (Add, Update, Remove, Get) - 4 tests")
    print("4. Booking API (Create, History) - 2 tests")
    print("5. Review API (Create, Get) - 2 tests")
    print("6. Address API (CRUD) - 2 tests")
    print("7. Admin Dashboard - 2 tests")
    print("8. Expiring/Expired Products - 2 tests")
    print("9. Top Customers - 1 test")
    print("10. Monthly Report - 1 test")
    print("11. Demand Forecast - 2 tests")
    print("12. Credit Scores - 2 tests")
    print("13. Review Analytics (NEW) - 2 tests")
    print("14. Offer Notifications (NEW) - 2 tests")
    print("=" * 60)
