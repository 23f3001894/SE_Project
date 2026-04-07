from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from backend.models import db
from backend.routes import auth_bp, product_bp, cart_bp, booking_bp, review_bp, address_bp, admin_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agriflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app)
    db.init_app(app)

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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)