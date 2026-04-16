import logging
import smtplib
from email.message import EmailMessage

from flask import current_app


logger = logging.getLogger(__name__)


def _is_email_enabled():
    if current_app.config.get("TESTING"):
        return False
    if current_app.config.get("MAIL_SUPPRESS_SEND"):
        return False
    return bool(current_app.config.get("MAIL_SERVER"))


def send_email(subject, recipients, body):
    if not recipients:
        return False

    if not _is_email_enabled():
        logger.info("Email skipped for %s: %s", recipients, subject)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    mail_server = current_app.config["MAIL_SERVER"]
    mail_port = current_app.config["MAIL_PORT"]
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    use_tls = current_app.config.get("MAIL_USE_TLS")
    use_ssl = current_app.config.get("MAIL_USE_SSL")

    try:
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with smtp_class(mail_server, mail_port, timeout=15) as smtp:
            if use_tls and not use_ssl:
                smtp.starttls()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
        return True
    except Exception as exc:
        logger.warning("Email delivery failed: %s", exc)
        return False


def _format_order_lines(booking):
    lines = []
    for item in booking.items:
        product_name = item.product.name if item.product else f"Product #{item.product_id}"
        lines.append(
            f"- {product_name}: {item.quantity} x Rs. {item.price_at_purchase:.2f}"
        )
    return "\n".join(lines)


def send_signup_email(user):
    body = (
        f"Hi {user.name},\n\n"
        f"Welcome to AgriFlow.\n"
        f"Your {user.role} account is ready and you can now sign in with {user.email}.\n\n"
        "Thank you for joining AgriFlow."
    )
    return send_email("Welcome to AgriFlow", [user.email], body)


def send_order_confirmation_email(customer, booking):
    body = (
        f"Hi {customer.name},\n\n"
        f"Your AgriFlow order #{booking.id} has been placed successfully.\n"
        f"Status: {booking.status}\n"
        f"Delivery date: {booking.delivery_date.date().isoformat() if booking.delivery_date else 'Not scheduled'}\n"
        f"Payment mode: {booking.mode_of_payment}\n"
        f"Total: Rs. {booking.total_price:.2f}\n\n"
        "Products:\n"
        f"{_format_order_lines(booking)}\n\n"
        "We will notify you when your order is delivered."
    )
    return send_email(f"AgriFlow Order #{booking.id} Confirmed", [customer.email], body)


def send_order_delivered_email(customer, booking):
    body = (
        f"Hi {customer.name},\n\n"
        f"Your AgriFlow order #{booking.id} has been marked as delivered.\n"
        f"Status: {booking.status}\n"
        f"Delivery date: {booking.delivery_date.date().isoformat() if booking.delivery_date else 'Completed'}\n"
        f"Total: Rs. {booking.total_price:.2f}\n\n"
        "Products:\n"
        f"{_format_order_lines(booking)}\n\n"
        "Thank you for shopping with AgriFlow."
    )
    return send_email(f"AgriFlow Order #{booking.id} Delivered", [customer.email], body)
