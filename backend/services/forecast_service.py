from collections import defaultdict
from datetime import UTC, datetime


def build_demand_forecast(product, bookings, months_ahead):
    monthly_sales = defaultdict(int)

    for booking in bookings:
        for item in booking.items:
            if item.product_id != product.id:
                continue
            year_month = booking.booking_date.strftime("%Y-%m")
            monthly_sales[year_month] += item.quantity

    sorted_months = sorted(monthly_sales.items())

    if len(sorted_months) < 3:
        if sorted_months:
            baseline = sum(quantity for _, quantity in sorted_months) / len(sorted_months)
            confidence = "low"
        else:
            baseline = max(1, product.quantity // 12)
            confidence = "low"
        method = "moving_average_fallback"
    else:
        trailing_values = [quantity for _, quantity in sorted_months[-3:]]
        baseline = sum(trailing_values) / len(trailing_values)
        confidence = "medium"
        method = "moving_average"

    forecast = []
    current_date = datetime.now(UTC)
    month_cursor = current_date.month
    year_cursor = current_date.year

    for index in range(months_ahead):
        month_cursor += 1
        if month_cursor == 13:
            month_cursor = 1
            year_cursor += 1

        seasonality_multiplier = 1 + (0.05 * min(index, 3))
        forecast.append(
            {
                "month": month_cursor,
                "year": year_cursor,
                "predicted_quantity": round(max(1, baseline * seasonality_multiplier)),
                "confidence": confidence,
            }
        )

    return {
        "product_id": product.id,
        "product_name": product.name,
        "forecast_period_months": months_ahead,
        "historical_data_points": len(sorted_months),
        "forecast": forecast,
        "method": method,
    }
