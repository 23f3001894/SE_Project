import json

from backend.models import Booking, Cart, CartItem, OfferNotification, Product, User, db
from conftest import seed_booking_for_customer, seed_offer_notification


class TestUserFunctionalFlows:
    def test_cart_enforces_single_seller_rule(
        self,
        client,
        auth_headers,
        customer_user,
        sample_product,
        second_admin_with_product,
    ):
        first_add = client.post(
            "/api/cart/add",
            data=json.dumps({"product_id": sample_product, "quantity": 1}),
            headers={**auth_headers, **customer_user},
        )
        assert first_add.status_code == 200

        second_add = client.post(
            "/api/cart/add",
            data=json.dumps(
                {"product_id": second_admin_with_product["product_id"], "quantity": 1}
            ),
            headers={**auth_headers, **customer_user},
        )
        assert second_add.status_code == 400
        assert "one seller" in json.loads(second_add.data)["message"].lower()

    def test_create_booking_updates_inventory_and_customer_metrics(
        self, client, app, auth_headers, customer_user, sample_product, customer_address
    ):
        add_res = client.post(
            "/api/cart/add",
            data=json.dumps({"product_id": sample_product, "quantity": 3}),
            headers={**auth_headers, **customer_user},
        )
        assert add_res.status_code == 200

        book_res = client.post(
            "/api/bookings/",
            data=json.dumps({"delivery_address_id": customer_address, "mode_of_payment": "Cash"}),
            headers={**auth_headers, **customer_user},
        )
        assert book_res.status_code == 201

        with app.app_context():
            product = db.session.get(Product, sample_product)
            customer = db.session.get(User, int(customer_user["X-User-ID"]))
            cart = Cart.query.filter_by(user_id=customer.id).first()
            assert product.quantity == 97
            assert product.no_of_orders == 3
            assert customer.no_of_orders == 1
            assert customer.total_spent == 150.0
            assert CartItem.query.filter_by(cart_id=cart.id).count() == 0

    def test_admin_can_only_deliver_owned_orders(
        self,
        client,
        app,
        auth_headers,
        admin_user,
        customer_user,
        sample_product,
        second_admin_with_product,
    ):
        valid_booking_id = seed_booking_for_customer(
            app,
            int(customer_user["X-User-ID"]),
            sample_product,
            quantity=2,
        )
        wrong_booking_id = seed_booking_for_customer(
            app,
            int(customer_user["X-User-ID"]),
            second_admin_with_product["product_id"],
            quantity=1,
        )

        ok_res = client.put(
            f"/api/admin/orders/{valid_booking_id}/deliver",
            headers={**auth_headers, **admin_user},
        )
        assert ok_res.status_code == 200

        forbidden_res = client.put(
            f"/api/admin/orders/{wrong_booking_id}/deliver",
            headers={**auth_headers, **admin_user},
        )
        assert forbidden_res.status_code == 403

        with app.app_context():
            booking = db.session.get(Booking, valid_booking_id)
            assert booking.status == "delivered"

    def test_offer_notification_read_flow_enforces_ownership(
        self, client, app, auth_headers, customer_user, second_customer, active_offer
    ):
        my_notification_id = seed_offer_notification(
            app, active_offer, int(customer_user["X-User-ID"])
        )
        other_notification_id = seed_offer_notification(
            app, active_offer, int(second_customer["X-User-ID"])
        )

        own_res = client.put(
            f"/api/bookings/notifications/offers/{my_notification_id}/read",
            headers={**auth_headers, **customer_user},
        )
        assert own_res.status_code == 200

        other_res = client.put(
            f"/api/bookings/notifications/offers/{other_notification_id}/read",
            headers={**auth_headers, **customer_user},
        )
        assert other_res.status_code == 403

        with app.app_context():
            mine = db.session.get(OfferNotification, my_notification_id)
            assert mine.is_read is True
            assert mine.read_at is not None


class TestAdminFunctionalFlows:
    def test_admin_product_management_workflow(
        self, client, app, auth_headers, admin_user, customer_user, sample_product
    ):
        # Admin creates a new product
        create_payload = {
            "name": "Fresh Apples",
            "description": "Organic apples",
            "quantity": 150,
            "price": 40.0,
            "expiry_date": "2026-12-31",
        }
        create_res = client.post(
            "/api/products/",
            data=json.dumps(create_payload),
            headers={**auth_headers, **admin_user},
        )
        assert create_res.status_code == 201
        data = json.loads(create_res.data)
        new_product_id = data["product_id"]

        # Admin updates the product
        update_payload = {"price": 45.0, "quantity": 160}
        update_res = client.put(
            f"/api/products/{new_product_id}",
            data=json.dumps(update_payload),
            headers={**auth_headers, **admin_user},
        )
        assert update_res.status_code == 200

        # Customer adds updated product to cart
        add_res = client.post(
            "/api/cart/add",
            data=json.dumps({"product_id": new_product_id, "quantity": 2}),
            headers={**auth_headers, **customer_user},
        )
        assert add_res.status_code == 200

        # Admin deletes the product
        delete_res = client.delete(
            f"/api/products/{new_product_id}",
            headers={**auth_headers, **admin_user},
        )
        assert delete_res.status_code == 200

        # Verify product is deleted
        with app.app_context():
            product = db.session.get(Product, new_product_id)
            assert product is None

    def test_admin_dashboard_and_reporting_workflow(
        self, client, app, auth_headers, admin_user, customer_user, sample_product, customer_address
    ):
        # Customer makes a purchase
        add_res = client.post(
            "/api/cart/add",
            data=json.dumps({"product_id": sample_product, "quantity": 1}),
            headers={**auth_headers, **customer_user},
        )
        assert add_res.status_code == 200

        book_res = client.post(
            "/api/bookings/",
            data=json.dumps({"delivery_address_id": customer_address, "mode_of_payment": "Cash"}),
            headers={**auth_headers, **customer_user},
        )
        assert book_res.status_code == 201

        # Admin checks dashboard stats
        stats_res = client.get(
            "/api/admin/dashboard/stats",
            headers={**auth_headers, **admin_user},
        )
        assert stats_res.status_code == 200
        stats_data = json.loads(stats_res.data)
        assert stats_data["total_orders"] >= 1
        assert stats_data["total_users"] >= 1

        # Admin checks monthly report
        report_res = client.get(
            "/api/admin/reports/monthly",
            headers={**auth_headers, **admin_user},
        )
        assert report_res.status_code == 200
        report_data = json.loads(report_res.data)
        assert "total_sales" in report_data
        assert "total_orders" in report_data

        # Admin checks top customers
        top_res = client.get(
            "/api/admin/customers/top",
            headers={**auth_headers, **admin_user},
        )
        assert top_res.status_code == 200
        top_data = json.loads(top_res.data)
        assert "top_customers" in top_data

    def test_admin_forecast_and_credit_management_workflow(
        self, client, app, auth_headers, admin_user, customer_user, sample_product
    ):
        # Admin gets demand forecast for a product
        forecast_res = client.get(
            f"/api/admin/forecast/demand?product_id={sample_product}&months_ahead=2",
            headers={**auth_headers, **admin_user},
        )
        assert forecast_res.status_code == 200
        forecast_data = json.loads(forecast_res.data)
        assert "forecast" in forecast_data
        assert len(forecast_data["forecast"]) == 2

        # Admin updates customer credit score
        update_credit_res = client.put(
            f"/api/admin/customers/{int(customer_user['X-User-ID'])}/credit-score",
            data=json.dumps({"credit_score": 85}),
            headers={**auth_headers, **admin_user},
        )
        assert update_credit_res.status_code == 200

        # Admin gets credit scores
        credit_res = client.get(
            "/api/admin/customers/credit-scores",
            headers={**auth_headers, **admin_user},
        )
        assert credit_res.status_code == 200
        credit_data = json.loads(credit_res.data)
        assert "customers" in credit_data

    def test_admin_offer_notification_workflow(
        self, client, app, auth_headers, admin_user, customer_user, active_offer
    ):
        # Admin sends notifications for an existing offer (using active_offer fixture)
        notify_res = client.post(
            "/api/admin/offers/send-notifications",
            data=json.dumps({"offer_id": active_offer}),
            headers={**auth_headers, **admin_user},
        )
        assert notify_res.status_code == 200
        notify_data = json.loads(notify_res.data)
        assert "notifications_sent" in notify_data

        # Customer checks their offer notifications
        notif_res = client.get(
            "/api/bookings/notifications/offers",
            headers={**auth_headers, **customer_user},
        )
        assert notif_res.status_code == 200
        notif_data = json.loads(notif_res.data)
        assert "offer_notifications" in notif_data
