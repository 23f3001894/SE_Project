from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    mobile_no = db.Column(db.String(15))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    no_of_orders = db.Column(db.Integer, default=0)
    role = db.Column(db.String(20), nullable=False)
    credit_score = db.Column(db.Integer, default=50)
    total_spent = db.Column(db.Float, default=0.0)
    total_paid = db.Column(db.Float, default=0.0)

    addresses = db.relationship('Address', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', uselist=False)

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address_line_1 = db.Column(db.String(200), nullable=False)
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'id', name='_user_address_uc'),)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    expiry_status = db.Column(db.String(20), default='valid')
    no_of_orders = db.Column(db.Integer, default=0)

    reviews = db.relationship('Review', backref='product', lazy=True)
    booking_items = db.relationship('BookingItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    delivery_date = db.Column(db.DateTime)
    mode_of_payment = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')

    delivery_address = db.relationship('Address', foreign_keys=[delivery_address_id])
    items = db.relationship('BookingItem', backref='booking', lazy=True)

class BookingItem(db.Model):
    __tablename__ = 'booking_items'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    __table_args__ = (db.UniqueConstraint('booking_id', 'product_id', name='_booking_product_uc'),)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy=True)

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('cart_id', 'product_id', name='_cart_product_uc'),)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'), nullable=True)

class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    usage_limit = db.Column(db.Integer, nullable=True)
    times_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product')

class OfferNotification(db.Model):
    __tablename__ = 'offer_notification'
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    offer = db.relationship('Offer', backref='offer_notifications')
    user = db.relationship('User', backref='user_offer_notifications')
