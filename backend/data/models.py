from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    mobile_no = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='user')
    last_login = db.Column(db.DateTime)
    user_orders = db.Column(db.Integer, default=0)

    addresses = db.relationship('Addresses', backref='user', lazy=True)
    bookings = db.relationship('Bookings', backref='user', lazy=True)
    reviews = db.relationship('Reviews', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', uselist=False)

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self):
        return {
            'id': self.user_id,
            'name': self.name,
            'email': self.email,
            'mobile_no': self.mobile_no,
            'role': self.role
        }


class Addresses(db.Model):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET DEFAULT'),
        primary_key=True,
        nullable=False,
        default=-1
    )

    address_line_1 = db.Column(db.String, nullable=False)
    address_line_2 = db.Column(db.String)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    pin = db.Column(db.String, nullable=False)
    default = db.Column(db.Boolean, default=False)

    bookings = db.relationship('Bookings', backref='delivery_address', lazy=True)

    def to_dict(self):
        return {
            'address_id': self.address_id,
            'user_id': self.user_id,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'pin': self.pin
        }


class Products(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)

    expiry_status = db.Column(db.Boolean, default=False)
    num_orders = db.Column(db.Integer, default=0)

    reviews = db.relationship('Reviews', backref='product', lazy=True)
    booking_items = db.relationship('BookingItems', backref='product', lazy=True)
    cart_items = db.relationship('CartItems', backref='product', lazy=True)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price
        }


class Reviews(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.product_id', ondelete='SET DEFAULT'),
        nullable=False,
        default=-1
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET DEFAULT'),
        nullable=False,
        default=-1
    )

    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'review_id': self.review_id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'review': self.review
        }


class Bookings(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET DEFAULT'),
        nullable=False,
        default=-1
    )

    delivery_address_id = db.Column(
        db.Integer,
        db.ForeignKey('addresses.address_id', ondelete='SET DEFAULT'),
        nullable=False,
        default=-1
    )

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime)

    total_price = db.Column(db.Float, nullable=False)

    mode_of_payment = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default='Order Placed')

    booking_items = db.relationship('BookingItems', backref='booking', lazy=True)

    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'booking_date': self.booking_date,
            'delivery_date': self.delivery_date,
            'total_price': self.total_price,
            'status': self.status
        }


class BookingItems(db.Model):
    __tablename__ = 'booking_items'

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey('bookings.booking_id', ondelete='SET DEFAULT'),
        primary_key=True,
        default=-1
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.product_id', ondelete='SET DEFAULT'),
        primary_key=True,
        default=-1
    )

    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase
        }


class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship(
        'CartItems',
        backref='cart',
        cascade='all, delete',
        lazy=True
    )

    def to_dict(self):
        return {
            'cart_id': self.cart_id,
            'user_id': self.user_id,
            'created_at': self.created_at
        }


class CartItems(db.Model):
    __tablename__ = 'cart_items'

    cart_id = db.Column(
        db.Integer,
        db.ForeignKey('cart.cart_id', ondelete='CASCADE'),
        primary_key=True
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.product_id', ondelete='SET DEFAULT'),
        primary_key=True,
        default=-1
    )

    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }