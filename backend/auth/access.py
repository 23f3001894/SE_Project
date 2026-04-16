from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

VALID_ROLES = {"customer", "admin"}


def get_current_user_id():
    identity = get_jwt_identity()
    return int(identity) if identity is not None else None


def get_current_user_role():
    return get_jwt().get("role")


def get_optional_user_role(default="customer"):
    verify_jwt_in_request(optional=True)
    identity = get_jwt_identity()
    if identity is None:
        return default
    return get_jwt().get("role", default)


def ensure_roles(*allowed_roles):
    verify_jwt_in_request()
    role = get_current_user_role()
    if role not in allowed_roles:
        return jsonify({"message": "Unauthorized"}), 403
    return None
