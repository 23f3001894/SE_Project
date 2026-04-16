from flask_jwt_extended import create_access_token

from backend.auth import VALID_ROLES
from backend.models import Cart, User, db

ROLE_ALIASES = {
    "admin": "admin",
    "seller": "admin",
    "customer": "customer",
    "user": "customer",
    "buyer": "customer",
}


def normalize_role(role):
    normalized = ROLE_ALIASES.get((role or "customer").strip().lower())
    if normalized not in VALID_ROLES:
        return None
    return normalized


def serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile_no": user.mobile_no,
        "role": user.role,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


def build_auth_payload(user):
    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "email": user.email,
            "name": user.name,
        },
    )
    return {
        "access_token": token,
        "user": serialize_user(user),
        "user_id": user.id,
        "role": user.role,
        "name": user.name,
    }


def ensure_user_cart(user):
    if not Cart.query.filter_by(user_id=user.id).first():
        db.session.add(Cart(user_id=user.id))


def create_user(name, email, password, mobile_no=None, role="customer"):
    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        mobile_no=mobile_no,
        role=role,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    ensure_user_cart(user)
    return user
