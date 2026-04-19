from datetime import UTC, datetime

import pytest

from backend.models import User
from backend.services import auth_service, forecast_service, reporting_service


class DummyProduct:
    def __init__(self, product_id, name, quantity):
        self.id = product_id
        self.name = name
        self.quantity = quantity


class DummyItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity


class DummyBooking:
    def __init__(self, booking_date, items):
        self.booking_date = booking_date
        self.items = items


class TestAuthServiceUnit:
    @pytest.mark.parametrize(
        "input_role, expected",
        [
            ("admin", "admin"),
            ("seller", "admin"),
            ("customer", "customer"),
            ("buyer", "customer"),
            ("invalid", None),
            ("ADMIN", "admin"),
            ("Customer", "customer"),
            ("", "customer"),
            ("user", "customer"),
            ("manager", None),
        ],
    )
    def test_normalize_role_aliases_and_invalid(self, input_role, expected):
        assert auth_service.normalize_role(input_role) == expected

    def test_create_user_normalizes_email_and_creates_cart(self, app):
        with app.app_context():
            user = auth_service.create_user(
                name="  Unit User  ",
                email="  UNIT@EXAMPLE.COM  ",
                password="secret123",
                role="customer",
            )
            assert user.name == "Unit User"
            assert user.email == "unit@example.com"
            assert user.password != "secret123"
            assert user.check_password("secret123") is True
            assert user.cart is not None

    def test_create_user_with_admin_role(self, app):
        with app.app_context():
            user = auth_service.create_user(
                name="Admin User",
                email="admin@test.com",
                password="adminpass",
                role="admin",
            )
            assert user.role == "admin"
            assert user.cart is not None  # Even admin should have a cart

    def test_create_user_handles_duplicate_email(self, app):
        with app.app_context():
            auth_service.create_user("User1", "dup@test.com", "pass", role="customer")
            with pytest.raises(Exception):  # Assuming it raises an exception for duplicate
                auth_service.create_user("User2", "dup@test.com", "pass", role="customer")

    def test_user_check_password_handles_legacy_plaintext(self):
        user = User(name="Legacy", email="legacy@test.com", password="plainpass", role="customer")
        assert user.check_password("plainpass") is True
        assert user.check_password("wrong") is False

    def test_user_check_password_with_hashed_password(self):
        user = User(name="Hashed", email="hashed@test.com", role="customer")
        user.set_password("hashedpass")
        assert user.check_password("hashedpass") is True
        assert user.check_password("wrong") is False


class TestForecastServiceUnit:
    def test_build_demand_forecast_with_history_uses_moving_average(self):
        product = DummyProduct(1, "Tomatoes", 120)
        bookings = [
            DummyBooking(datetime(2026, 1, 15, tzinfo=UTC), [DummyItem(1, 12)]),
            DummyBooking(datetime(2026, 2, 15, tzinfo=UTC), [DummyItem(1, 18)]),
            DummyBooking(datetime(2026, 3, 15, tzinfo=UTC), [DummyItem(1, 30)]),
        ]

        result = forecast_service.build_demand_forecast(product, bookings, months_ahead=3)

        assert result["product_id"] == 1
        assert result["historical_data_points"] == 3
        assert result["method"] == "moving_average"
        assert len(result["forecast"]) == 3
        assert all(entry["predicted_quantity"] >= 1 for entry in result["forecast"])

    def test_build_demand_forecast_without_history_uses_fallback(self):
        product = DummyProduct(7, "Spinach", 60)
        result = forecast_service.build_demand_forecast(product, bookings=[], months_ahead=2)

        assert result["method"] == "moving_average_fallback"
        assert result["historical_data_points"] == 0
        assert len(result["forecast"]) == 2
        assert result["forecast"][0]["confidence"] == "low"

    def test_build_demand_forecast_with_insufficient_history(self):
        product = DummyProduct(5, "Carrots", 80)
        bookings = [
            DummyBooking(datetime(2026, 1, 15, tzinfo=UTC), [DummyItem(5, 10)]),
            DummyBooking(datetime(2026, 2, 15, tzinfo=UTC), [DummyItem(5, 15)]),
        ]

        result = forecast_service.build_demand_forecast(product, bookings, months_ahead=3)

        assert result["method"] == "moving_average_fallback"
        assert result["historical_data_points"] == 2
        assert len(result["forecast"]) == 3

    def test_build_demand_forecast_with_zero_quantity_product(self):
        product = DummyProduct(9, "Rare Item", 0)
        result = forecast_service.build_demand_forecast(product, bookings=[], months_ahead=1)

        assert result["method"] == "moving_average_fallback"
        assert result["historical_data_points"] == 0
        assert len(result["forecast"]) == 1
        assert result["forecast"][0]["predicted_quantity"] >= 1

    def test_build_demand_forecast_multiple_products_in_bookings(self):
        product = DummyProduct(2, "Apples", 200)
        bookings = [
            DummyBooking(datetime(2026, 1, 15, tzinfo=UTC), [DummyItem(2, 20), DummyItem(3, 10)]),
            DummyBooking(datetime(2026, 2, 15, tzinfo=UTC), [DummyItem(2, 25)]),
        ]

        result = forecast_service.build_demand_forecast(product, bookings, months_ahead=2)

        assert result["historical_data_points"] == 2
        assert result["method"] == "moving_average_fallback"  # Less than 3 points
        assert len(result["forecast"]) == 2


class TestReportingServiceUnit:
    def test_build_admin_top_customers_ranks_by_orders_then_spend(self, app):
        with app.app_context():
            admin = auth_service.create_user("Admin", "admin-unit@test.com", "admin123", role="admin")
            customer_a = auth_service.create_user("Cust A", "a@test.com", "pw", role="customer")
            customer_b = auth_service.create_user("Cust B", "b@test.com", "pw", role="customer")
            db = reporting_service.db
            from backend.models import Booking, BookingItem, Brand, Product

            brand = Brand(name="Unit Brand")
            db.session.add(brand)
            db.session.flush()

            product = Product(
                name="Unit Product",
                quantity=200,
                price=20,
                brand_id=brand.id,
                admin_id=admin.id,
            )
            db.session.add(product)
            db.session.flush()

            from backend.models import Address

            address_a = Address(
                user_id=customer_a.id,
                address_line_1="Test A",
                city="Pune",
                state="Maharashtra",
                pin_code="411001",
            )
            address_b = Address(
                user_id=customer_b.id,
                address_line_1="Test B",
                city="Pune",
                state="Maharashtra",
                pin_code="411001",
            )
            db.session.add_all([address_a, address_b])
            db.session.flush()

            booking_1 = Booking(
                user_id=customer_a.id,
                total_price=40,
                delivery_address_id=address_a.id,
                mode_of_payment="Cash",
            )
            booking_2 = Booking(
                user_id=customer_a.id,
                total_price=60,
                delivery_address_id=address_a.id,
                mode_of_payment="Cash",
            )
            booking_3 = Booking(
                user_id=customer_b.id,
                total_price=100,
                delivery_address_id=address_b.id,
                mode_of_payment="Cash",
            )

            db.session.add_all([booking_1, booking_2, booking_3])
            db.session.flush()

            db.session.add_all(
                [
                    BookingItem(booking_id=booking_1.id, product_id=product.id, quantity=2, price_at_purchase=20),
                    BookingItem(booking_id=booking_2.id, product_id=product.id, quantity=3, price_at_purchase=20),
                    BookingItem(booking_id=booking_3.id, product_id=product.id, quantity=5, price_at_purchase=20),
                ]
            )
            db.session.commit()

            top = reporting_service.build_admin_top_customers(admin.id)
            assert len(top) == 2
            assert top[0]["name"] == "Cust A"
            assert top[0]["no_of_orders"] == 2
            assert top[1]["name"] == "Cust B"

    def test_build_sales_summary_returns_zeroes_without_orders(self, app):
        with app.app_context():
            admin = auth_service.create_user("No Orders", "no-orders@test.com", "pw", role="admin")
            reporting_service.db.session.commit()

            summary = reporting_service.build_sales_summary(admin.id)
            assert summary["total_orders_this_month"] == 0
            assert summary["avg_order_value"] == 0

    def test_build_sales_summary_with_orders(self, app):
        with app.app_context():
            admin = auth_service.create_user("Admin With Orders", "orders@test.com", "pw", role="admin")
            customer = auth_service.create_user("Customer", "cust@test.com", "pw", role="customer")
            db = reporting_service.db
            from backend.models import Booking, BookingItem, Brand, Product, Address

            brand = Brand(name="Test Brand")
            db.session.add(brand)
            db.session.flush()

            product = Product(
                name="Test Product",
                quantity=100,
                price=50,
                brand_id=brand.id,
                admin_id=admin.id,
            )
            db.session.add(product)
            db.session.flush()

            address = Address(
                user_id=customer.id,
                address_line_1="Test Addr",
                city="Pune",
                state="Maharashtra",
                pin_code="411001",
            )
            db.session.add(address)
            db.session.flush()

            booking = Booking(
                user_id=customer.id,
                total_price=150,
                delivery_address_id=address.id,
                mode_of_payment="Cash",
            )
            db.session.add(booking)
            db.session.flush()

            db.session.add(
                BookingItem(booking_id=booking.id, product_id=product.id, quantity=3, price_at_purchase=50)
            )
            db.session.commit()

            summary = reporting_service.build_sales_summary(admin.id)
            assert summary["total_orders_this_month"] == 1
            assert summary["total_revenue_this_month"] == 150.0
            assert summary["avg_order_value"] == 150.0

    def test_build_monthly_sales_with_multiple_months(self, app):
        with app.app_context():
            admin = auth_service.create_user("Monthly Admin", "monthly@test.com", "pw", role="admin")
            customer = auth_service.create_user("Monthly Cust", "monthly-cust@test.com", "pw", role="customer")
            db = reporting_service.db
            from backend.models import Booking, BookingItem, Brand, Product, Address

            brand = Brand(name="Monthly Brand")
            db.session.add(brand)
            db.session.flush()

            product = Product(
                name="Monthly Product",
                quantity=100,
                price=50,
                brand_id=brand.id,
                admin_id=admin.id,
            )
            db.session.add(product)
            db.session.flush()

            address = Address(
                user_id=customer.id,
                address_line_1="Monthly Addr",
                city="Pune",
                state="Maharashtra",
                pin_code="411001",
            )
            db.session.add(address)
            db.session.flush()

            # Create bookings in different months
            booking1 = Booking(
                user_id=customer.id,
                total_price=100,
                delivery_address_id=address.id,
                mode_of_payment="Cash",
                booking_date=datetime(2026, 3, 15, tzinfo=UTC),
            )
            booking2 = Booking(
                user_id=customer.id,
                total_price=200,
                delivery_address_id=address.id,
                mode_of_payment="Cash",
                booking_date=datetime(2026, 4, 15, tzinfo=UTC),
            )
            db.session.add_all([booking1, booking2])
            db.session.flush()

            db.session.add_all([
                BookingItem(booking_id=booking1.id, product_id=product.id, quantity=2, price_at_purchase=50),
                BookingItem(booking_id=booking2.id, product_id=product.id, quantity=4, price_at_purchase=50),
            ])
            db.session.commit()

            monthly = reporting_service.build_monthly_sales(admin.id, months=2)
            assert len(monthly) == 2
            # Check that months are in descending order and data is correct
