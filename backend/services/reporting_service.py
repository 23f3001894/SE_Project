from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import func

from backend.models import Booking, BookingItem, Product, User, db


def get_admin_product_ids(admin_id):
    rows = db.session.query(Product.id).filter(Product.admin_id == admin_id).all()
    return [row[0] for row in rows]


def get_admin_bookings(admin_id):
    return (
        Booking.query.join(BookingItem, BookingItem.booking_id == Booking.id)
        .join(Product, Product.id == BookingItem.product_id)
        .filter(Product.admin_id == admin_id)
        .order_by(Booking.booking_date.desc())
        .distinct()
        .all()
    )


def get_admin_booking_items(admin_id):
    return (
        db.session.query(BookingItem, Booking)
        .join(Booking, Booking.id == BookingItem.booking_id)
        .join(Product, Product.id == BookingItem.product_id)
        .filter(Product.admin_id == admin_id)
        .all()
    )


def build_admin_top_customers(admin_id, limit=10):
    bookings = get_admin_bookings(admin_id)
    spending = defaultdict(lambda: {"orders": 0, "spent": 0.0})

    for booking in bookings:
        spending[booking.user_id]["orders"] += 1
        for item in booking.items:
            if item.product and item.product.admin_id == admin_id:
                spending[booking.user_id]["spent"] += item.quantity * item.price_at_purchase

    ranked = sorted(
        spending.items(),
        key=lambda item: (item[1]["orders"], item[1]["spent"]),
        reverse=True,
    )[:limit]

    output = []
    for user_id, aggregates in ranked:
        user = db.session.get(User, user_id)
        if not user:
            continue
        output.append(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "no_of_orders": aggregates["orders"],
                "total_spent": round(aggregates["spent"], 2),
            }
        )
    return output


def build_monthly_sales(admin_id, months=6):
    today = datetime.now(UTC)
    series = []

    for offset in range(months - 1, -1, -1):
        month_anchor = (today.replace(day=1) - timedelta(days=offset * 30)).replace(day=1)
        month = month_anchor.month
        year = month_anchor.year

        month_items = []
        for booking_item, booking in get_admin_booking_items(admin_id):
            if booking.booking_date.month == month and booking.booking_date.year == year:
                month_items.append((booking_item, booking))

        revenue = sum(item.quantity * item.price_at_purchase for item, _ in month_items)
        order_count = len({booking.id for _, booking in month_items})
        series.append(
            {
                "month": f"{month_anchor.strftime('%b')} {year}",
                "revenue": round(revenue, 2),
                "orders": order_count,
            }
        )

    previous_revenue = None
    for month_data in series:
        if previous_revenue in (None, 0):
            month_data["growth"] = 0
        else:
            month_data["growth"] = round(
                ((month_data["revenue"] - previous_revenue) / previous_revenue) * 100,
                1,
            )
        previous_revenue = month_data["revenue"]

    return series


def build_daily_sales(admin_id, days=7):
    today = datetime.now(UTC)
    series = []

    for offset in range(days - 1, -1, -1):
        day_anchor = (today - timedelta(days=offset)).date()
        day_items = []
        for booking_item, booking in get_admin_booking_items(admin_id):
            if booking.booking_date.date() == day_anchor:
                day_items.append((booking_item, booking))

        revenue = sum(item.quantity * item.price_at_purchase for item, _ in day_items)
        orders = len({booking.id for _, booking in day_items})
        series.append(
            {
                "date": day_anchor.isoformat(),
                "revenue": round(revenue, 2),
                "orders": orders,
            }
        )

    return series


def build_sales_summary(admin_id):
    monthly_sales = build_monthly_sales(admin_id)
    bookings = get_admin_bookings(admin_id)
    total_revenue_all_time = 0.0

    for booking in bookings:
        for item in booking.items:
            if item.product and item.product.admin_id == admin_id:
                total_revenue_all_time += item.quantity * item.price_at_purchase

    total_orders = len(bookings)
    latest_month = monthly_sales[-1] if monthly_sales else {"revenue": 0, "orders": 0}

    return {
        "total_revenue_this_month": latest_month["revenue"],
        "total_orders_this_month": latest_month["orders"],
        "avg_order_value": round(total_revenue_all_time / total_orders, 2) if total_orders else 0,
        "total_revenue_all_time": round(total_revenue_all_time, 2),
    }
