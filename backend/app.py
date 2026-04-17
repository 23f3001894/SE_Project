from pathlib import Path
import sys

from flask import Flask
from flask_cors import CORS
from sqlalchemy import inspect, text

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.auth.extensions import jwt
from backend.auth.extensions import bcrypt
from backend.config import Config
from backend.models import Brand, db
from backend.routes import auth_bp, product_bp, cart_bp, booking_bp, review_bp, address_bp, admin_bp


def ensure_legacy_schema_compatibility():
    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())

    if 'products' in table_names:
        product_columns = {column['name'] for column in inspector.get_columns('products')}
        schema_updates = []

        if 'image_path' not in product_columns:
            schema_updates.append(
                "ALTER TABLE products ADD COLUMN image_path VARCHAR(255)"
            )
        if 'brand_id' not in product_columns:
            schema_updates.append("ALTER TABLE products ADD COLUMN brand_id INTEGER")
        if 'admin_id' not in product_columns:
            schema_updates.append("ALTER TABLE products ADD COLUMN admin_id INTEGER")

        for statement in schema_updates:
            db.session.execute(text(statement))
        if schema_updates:
            db.session.commit()

    if 'brands' not in table_names:
        db.create_all()

    default_brand = Brand.query.filter_by(name='AgriFlow Select').first()
    if not default_brand:
        default_brand = Brand(name='AgriFlow Select')
        db.session.add(default_brand)
        db.session.commit()

    first_admin_id = db.session.execute(
        text("SELECT id FROM user WHERE role = 'admin' ORDER BY id LIMIT 1")
    ).scalar()

    db.session.execute(
        text(
            """
            UPDATE products
            SET image_path = :image_path
            WHERE image_path IS NULL OR image_path = ''
            """
        ),
        {"image_path": "/static/images/product-placeholder.svg"},
    )

    db.session.execute(
        text(
            """
            UPDATE products
            SET brand_id = :brand_id
            WHERE brand_id IS NULL
            """
        ),
        {"brand_id": default_brand.id},
    )

    if first_admin_id:
        db.session.execute(
            text(
                """
                UPDATE products
                SET admin_id = :admin_id
                WHERE admin_id IS NULL
                """
            ),
            {"admin_id": first_admin_id},
        )

    db.session.commit()

def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
    
    CORS(app, resources={r'/api/*': {'origins': '*'}}, allow_headers=['Content-Type', 'Authorization'])
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    @jwt.user_lookup_loader
    def load_user(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        from backend.models import User

        return db.session.get(User, int(identity))

    @jwt.unauthorized_loader
    def unauthorized_loader(_reason):
        return {'message': 'Authentication required'}, 401

    @jwt.invalid_token_loader
    def invalid_token_loader(_reason):
        return {'message': 'Invalid authentication token'}, 401

    @jwt.expired_token_loader
    def expired_token_loader(_jwt_header, _jwt_payload):
        return {'message': 'Authentication token has expired'}, 401

    @jwt.user_lookup_error_loader
    def user_lookup_error_loader(_jwt_header, _jwt_payload):
        return {'message': 'Authenticated user no longer exists'}, 401

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(address_bp, url_prefix='/api/addresses')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    with app.app_context():
        db.create_all()  # Create tables
        ensure_legacy_schema_compatibility()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
