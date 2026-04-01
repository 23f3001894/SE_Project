"""
AgriFlow Backend API
Flask-based REST API for the AgriFlow agricultural e-commerce platform
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}}, supports_credentials=True)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agriflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'agriflow-secret-key-2024')

# Initialize database
db = SQLAlchemy(app)


# =============================================================================
# DATABASE MODELS (aligned with models.py)
# =============================================================================

class Users(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    mobile_no = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='customer')
    last_login = db.Column(db.DateTime)
    user_orders = db.Column(db.Integer, default=0)

    addresses = db.relationship('Addresses', backref='user', lazy=True)
    bookings = db.relationship('Bookings', backref='user', lazy=True)
    reviews = db.relationship('Reviews', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', uselist=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'mobile_no': self.mobile_no,
            'role': self.role
        }


class Addresses(db.Model):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )
    address_line_1 = db.Column(db.String, nullable=False)
    address_line_2 = db.Column(db.String)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    pin = db.Column(db.String, nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'address_id': self.address_id,
            'user_id': self.user_id,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'pin': self.pin,
            'is_default': self.is_default
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
    expiry_status = db.Column(db.String, default='valid')
    num_orders = db.Column(db.Integer, default=0)
    category = db.Column(db.String)

    reviews = db.relationship('Reviews', backref='product', lazy=True)
    booking_items = db.relationship('BookingItems', backref='product', lazy=True)
    cart_items = db.relationship('CartItems', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.product_id,
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price,
            'date_added': self.date_added.isoformat() if self.date_added else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'expiry_status': self.get_expiry_status(),
            'num_orders': self.num_orders,
            'category': self.category
        }

    def get_expiry_status(self):
        if not self.expiry_date:
            return 'valid'
        now = datetime.utcnow()
        diff = self.expiry_date - now
        if diff.days < 0:
            return 'expired'
        elif diff.days <= 14:
            return 'expiring_soon'
        return 'valid'


class Reviews(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.product_id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'review_id': self.review_id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Bookings(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )
    delivery_address_id = db.Column(
        db.Integer,
        db.ForeignKey('addresses.address_id', ondelete='SET NULL'),
        nullable=True
    )
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime)
    total_price = db.Column(db.Float, nullable=False)
    mode_of_payment = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default='Order Placed')

    booking_items = db.relationship('BookingItems', backref='booking', lazy=True)
    delivery_address = db.relationship('Addresses', foreign_keys=[delivery_address_id])

    def to_dict(self, include_items=True):
        result = {
            'id': self.booking_id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'customer_name': self.user.name if self.user else 'Unknown',
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'total_price': self.total_price,
            'mode_of_payment': self.mode_of_payment,
            'status': self.status,
            'delivery_address': self.delivery_address.to_dict() if self.delivery_address else None
        }
        if include_items:
            result['items'] = [item.to_dict() for item in self.booking_items]
        return result


class BookingItems(db.Model):
    __tablename__ = 'booking_items'

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey('bookings.booking_id', ondelete='CASCADE'),
        primary_key=True
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.product_id', ondelete='CASCADE'),
        primary_key=True
    )
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'quantity': self.quantity,
            'total_price': self.price_at_purchase * self.quantity
        }


class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship(
        'CartItems',
        backref='cart',
        cascade='all, delete',
        lazy=True
    )


class CartItems(db.Model):
    __tablename__ = 'cart_items'

    cart_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(
        db.Integer,
        db.ForeignKey('cart.cart_id', ondelete='CASCADE'),
        nullable=False
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.product_id', ondelete='CASCADE'),
        nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'cart_item_id': self.cart_item_id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'price': self.product.price if self.product else 0,
            'quantity': self.quantity,
            'total_price': (self.product.price * self.quantity) if self.product else 0
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed


def get_user_from_request():
    """Extract user info from request headers"""
    user_id = request.headers.get('User-Id')
    role = request.headers.get('Role')
    if user_id:
        user_id = int(user_id)
    return user_id, role


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, role = get_user_from_request()
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        # Pass user_id and role as keyword arguments to avoid conflict with URL params
        kwargs['user_id'] = user_id
        kwargs['role'] = role
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, role = get_user_from_request()
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        if role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        # Pass user_id and role as keyword arguments to avoid conflict with URL params
        kwargs['user_id'] = user_id
        kwargs['role'] = role
        return f(*args, **kwargs)
    return decorated


# =============================================================================
# CORS PREFLIGHT HANDLER
# =============================================================================

@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """Handle OPTIONS preflight requests for CORS"""
    return '', 204

# =============================================================================
# AUTH ENDPOINTS
# =============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = Users.query.filter_by(email=email).first()

    if not user or not verify_password(password, user.password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'email': user.email,
        'mobile_no': user.mobile_no,
        'role': user.role
    })


@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()

    required_fields = ['name', 'email', 'password', 'mobile_no']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400

    # Check if email already exists
    if Users.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 409

    # Create new user
    new_user = Users(
        name=data['name'],
        email=data['email'],
        password=hash_password(data['password']),
        mobile_no=data['mobile_no'],
        role=data.get('role', 'customer')
    )

    db.session.add(new_user)
    db.session.commit()

    # Create cart for the new user
    cart = Cart(user_id=new_user.user_id)
    db.session.add(cart)
    db.session.commit()

    return jsonify({'message': 'Registration successful! Please login.'})


# =============================================================================
# PRODUCTS ENDPOINTS
# =============================================================================

@app.route('/api/products/', methods=['GET'])
def get_products():
    """Get all products"""
    products = Products.query.all()
    return jsonify({
        'products': [p.to_dict() for p in products]
    })


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify({'product': product.to_dict()})


@app.route('/api/products/', methods=['POST'])
@require_admin
def create_product(user_id, role):
    """Create a new product (Admin only)"""
    data = request.get_json()

    required_fields = ['name', 'quantity', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400

    product = Products(
        name=data['name'],
        description=data.get('description', ''),
        quantity=data['quantity'],
        price=data['price'],
        expiry_date=datetime.fromisoformat(data['expiry_date']) if data.get('expiry_date') else None,
        category=data.get('category', 'General')
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201


@app.route('/api/products/<int:product_id>', methods=['PUT'])
@require_admin
def update_product(product_id, user_id, role):
    """Update a product (Admin only)"""
    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    data = request.get_json()

    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'quantity' in data:
        product.quantity = data['quantity']
    if 'price' in data:
        product.price = data['price']
    if 'expiry_date' in data:
        product.expiry_date = datetime.fromisoformat(data['expiry_date']) if data['expiry_date'] else None
    if 'category' in data:
        product.category = data['category']

    db.session.commit()

    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    })


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@require_admin
def delete_product(product_id, user_id, role):
    """Delete a product (Admin only)"""
    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Delete related records first (reviews, cart items, booking items)
    # These are defined in this file, no import needed
    
    # Delete reviews for this product
    Reviews.query.filter_by(product_id=product_id).delete()
    
    # Delete cart items for this product
    CartItems.query.filter_by(product_id=product_id).delete()
    
    # Delete booking items for this product (just the links, not the bookings)
    BookingItems.query.filter_by(product_id=product_id).delete()
    
    # Now delete the product
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'})


# =============================================================================
# CART ENDPOINTS
# =============================================================================

@app.route('/api/cart/', methods=['GET'])
@require_auth
def get_cart(user_id, role):
    """Get user's cart"""
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    cart_items = CartItems.query.filter_by(cart_id=cart.cart_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items if item.product)

    return jsonify({
        'cart_items': [item.to_dict() for item in cart_items],
        'total_price': total_price
    })


@app.route('/api/cart/add', methods=['POST'])
@require_auth
def add_to_cart(user_id, role):
    """Add item to cart"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'message': 'product_id is required'}), 400

    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Get or create cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    # Check if item already in cart
    cart_item = CartItems.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItems(
            cart_id=cart.cart_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({'message': 'Item added to cart'})


@app.route('/api/cart/update/<int:cart_item_id>', methods=['PUT'])
@require_auth
def update_cart_item(cart_item_id, user_id, role):
    """Update cart item quantity"""
    data = request.get_json()
    quantity = data.get('quantity', 0)

    cart_item = CartItems.query.get(cart_item_id)
    if not cart_item or cart_item.cart.user_id != user_id:
        return jsonify({'message': 'Item not found in cart'}), 404

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()

    return jsonify({'message': 'Cart updated'})


@app.route('/api/cart/remove/<int:cart_item_id>', methods=['DELETE'])
@require_auth
def remove_from_cart(cart_item_id, user_id, role):
    """Remove item from cart"""
    cart_item = CartItems.query.get(cart_item_id)
    if not cart_item or cart_item.cart.user_id != user_id:
        return jsonify({'message': 'Item not found in cart'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'Item removed from cart'})


# =============================================================================
# BOOKINGS/ORDERS ENDPOINTS
# =============================================================================

@app.route('/api/bookings/history', methods=['GET'])
@require_auth
def get_booking_history(user_id, role):
    """Get user's booking history"""
    if role == 'admin':
        bookings = Bookings.query.all()
    else:
        bookings = Bookings.query.filter_by(user_id=user_id).all()

    return jsonify({
        'bookings': [b.to_dict() for b in bookings]
    })


@app.route('/api/bookings/', methods=['POST'])
@require_auth
def create_booking(user_id, role):
    """Create a new booking (place order)"""
    data = request.get_json()

    # Get user's cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({'message': 'Cart is empty'}), 400

    cart_items = CartItems.query.filter_by(cart_id=cart.cart_id).all()
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400

    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cart_items if item.product)

    # Create booking
    booking = Bookings(
        user_id=user_id,
        delivery_address_id=data.get('delivery_address_id'),
        delivery_date=datetime.fromisoformat(data['delivery_date']) if data.get('delivery_date') else None,
        total_price=total_price,
        mode_of_payment=data.get('mode_of_payment', 'cash'),
        status='Order Placed'
    )

    db.session.add(booking)
    db.session.commit()

    # Create booking items and update product quantities
    for item in cart_items:
        if item.product:
            booking_item = BookingItems(
                booking_id=booking.booking_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            db.session.add(booking_item)

            # Update product quantity and order count
            item.product.quantity = max(0, item.product.quantity - item.quantity)
            item.product.num_orders += item.quantity

    # Update user's order count
    user = Users.query.get(user_id)
    if user:
        user.user_orders += 1

    # Clear cart
    CartItems.query.filter_by(cart_id=cart.cart_id).delete()
    db.session.commit()

    return jsonify({
        'message': 'Order placed successfully',
        'booking_id': booking.booking_id,
        'total_price': booking.total_price
    }), 201


# =============================================================================
# ADDRESSES ENDPOINTS
# =============================================================================

@app.route('/api/addresses/', methods=['GET'])
@require_auth
def get_addresses(user_id, role):
    """Get user's addresses"""
    addresses = Addresses.query.filter_by(user_id=user_id).all()
    return jsonify({
        'addresses': [a.to_dict() for a in addresses]
    })


@app.route('/api/addresses/', methods=['POST'])
@require_auth
def create_address(user_id, role):
    """Create a new address"""
    data = request.get_json()

    required_fields = ['address_line_1', 'city', 'state', 'pin']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400

    # Check if this is the first address (make it default)
    existing_addresses = Addresses.query.filter_by(user_id=user_id).count()
    is_default = existing_addresses == 0 or data.get('is_default', False)

    # If setting as default, unset other defaults
    if is_default:
        Addresses.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})

    address = Addresses(
        user_id=user_id,
        address_line_1=data['address_line_1'],
        address_line_2=data.get('address_line_2', ''),
        city=data['city'],
        state=data['state'],
        pin=data['pin'],
        is_default=is_default
    )

    db.session.add(address)
    db.session.commit()

    return jsonify({
        'message': 'Address saved successfully',
        'address': address.to_dict()
    }), 201


@app.route('/api/addresses/<int:address_id>', methods=['PUT'])
@require_auth
def update_address(address_id, user_id, role):
    """Update an address"""
    address = Addresses.query.filter_by(address_id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({'message': 'Address not found'}), 404

    data = request.get_json()

    if 'address_line_1' in data:
        address.address_line_1 = data['address_line_1']
    if 'address_line_2' in data:
        address.address_line_2 = data['address_line_2']
    if 'city' in data:
        address.city = data['city']
    if 'state' in data:
        address.state = data['state']
    if 'pin' in data:
        address.pin = data['pin']

    # Handle default setting
    if data.get('is_default'):
        Addresses.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        address.is_default = True

    db.session.commit()

    return jsonify({'message': 'Address updated successfully'})


@app.route('/api/addresses/<int:address_id>', methods=['DELETE'])
@require_auth
def delete_address(address_id, user_id, role):
    """Delete an address"""
    address = Addresses.query.filter_by(address_id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({'message': 'Address not found'}), 404

    db.session.delete(address)
    db.session.commit()

    return jsonify({'message': 'Address deleted successfully'})


# =============================================================================
# REVIEWS ENDPOINTS
# =============================================================================

@app.route('/api/reviews/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Get reviews for a product"""
    reviews = Reviews.query.filter_by(product_id=product_id).all()
    return jsonify({
        'reviews': [r.to_dict() for r in reviews]
    })


@app.route('/api/reviews/', methods=['POST'])
@require_auth
def create_review(user_id, role):
    """Create a review for a product"""
    data = request.get_json()

    product_id = data.get('product_id')
    rating = data.get('rating')

    if not product_id or not rating:
        return jsonify({'message': 'product_id and rating are required'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400

    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    review = Reviews(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        review=data.get('review', '')
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        'message': 'Review added successfully',
        'review': review.to_dict()
    }), 201


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

@app.route('/api/admin/dashboard/stats', methods=['GET'])
@require_admin
def get_dashboard_stats(user_id, role):
    """Get dashboard statistics"""
    total_products = Products.query.count()
    total_users = Users.query.filter_by(role='customer').count()
    total_orders = Bookings.query.count()

    # Calculate expiring soon and expired products
    now = datetime.utcnow()
    expiring_soon = Products.query.filter(
        Products.expiry_date != None,
        Products.expiry_date <= now + timedelta(days=14),
        Products.expiry_date > now
    ).count()

    expired = Products.query.filter(
        Products.expiry_date != None,
        Products.expiry_date < now
    ).count()

    # Low stock (less than 10 units)
    low_stock = Products.query.filter(Products.quantity < 10).count()

    return jsonify({
        'total_products': total_products,
        'total_users': total_users,
        'total_orders': total_orders,
        'expiring_soon': expiring_soon,
        'expired_products': expired,
        'low_stock': low_stock
    })


@app.route('/api/admin/products/expiring', methods=['GET'])
@require_admin
def get_expiring_products(user_id, role):
    """Get products expiring soon"""
    now = datetime.utcnow()
    products = Products.query.filter(
        Products.expiry_date != None,
        Products.expiry_date <= now + timedelta(days=14),
        Products.expiry_date > now
    ).all()

    result = []
    for p in products:
        product_dict = p.to_dict()
        diff = p.expiry_date - now
        product_dict['days_until_expiry'] = diff.days
        result.append(product_dict)

    return jsonify({'expiring_products': result})


@app.route('/api/admin/products/expired', methods=['GET'])
@require_admin
def get_expired_products(user_id, role):
    """Get expired products"""
    now = datetime.utcnow()
    products = Products.query.filter(
        Products.expiry_date != None,
        Products.expiry_date < now
    ).all()

    return jsonify({
        'expired_products': [p.to_dict() for p in products]
    })


@app.route('/api/admin/customers/top', methods=['GET'])
@require_admin
def get_top_customers(user_id, role):
    """Get top customers by orders"""
    customers = Users.query.filter_by(role='customer').order_by(Users.user_orders.desc()).limit(10).all()

    result = []
    for c in customers:
        total_spent = db.session.query(db.func.sum(Bookings.total_price)).filter(
            Bookings.user_id == c.user_id
        ).scalar() or 0

        result.append({
            'id': c.user_id,
            'name': c.name,
            'email': c.email,
            'no_of_orders': c.user_orders,
            'total_spent': total_spent
        })

    return jsonify({'top_customers': result})


@app.route('/api/admin/customers/credit-scores', methods=['GET'])
@require_admin
def get_credit_scores(user_id, role):
    """Get customer credit scores"""
    customers = Users.query.filter_by(role='customer').all()

    result = []
    for c in customers:
        total_spent = db.session.query(db.func.sum(Bookings.total_price)).filter(
            Bookings.user_id == c.user_id,
            Bookings.status.in_(['Delivered', 'delivered', 'completed'])
        ).scalar() or 0

        total_paid = db.session.query(db.func.sum(Bookings.total_price)).filter(
            Bookings.user_id == c.user_id,
            Bookings.mode_of_payment == 'cash'
        ).scalar() or 0

        result.append({
            'id': c.user_id,
            'name': c.name,
            'total_spent': total_spent,
            'total_paid': total_paid
        })

    return jsonify({'customers': result})


@app.route('/api/admin/recommendations/high-demand', methods=['GET'])
@require_admin
def get_high_demand_recommendations(user_id, role):
    """Get high demand product recommendations"""
    products = Products.query.order_by(Products.num_orders.desc()).limit(10).all()

    result = []
    for p in products:
        demand_level = 'high' if p.num_orders > 20 else 'medium' if p.num_orders > 10 else 'low'
        action = 'Increase stock by 50%' if demand_level == 'high' else 'Maintain current stock levels'

        result.append({
            'product_id': p.product_id,
            'product_name': p.name,
            'units_sold_last_30_days': p.num_orders,
            'demand_level': demand_level,
            'recommended_action': action
        })

    return jsonify({'high_demand_recommendations': result})


# =============================================================================
# SALES REPORTS ENDPOINTS
# =============================================================================

@app.route('/api/admin/reports/monthly-sales', methods=['GET'])
@require_admin
def get_monthly_sales(user_id, role):
    """Get monthly sales report"""
    # Group bookings by month
    from sqlalchemy import func, extract

    monthly_data = db.session.query(
        extract('month', Bookings.booking_date).label('month'),
        extract('year', Bookings.booking_date).label('year'),
        func.sum(Bookings.total_price).label('revenue'),
        func.count(Bookings.booking_id).label('orders')
    ).group_by(
        extract('year', Bookings.booking_date),
        extract('month', Bookings.booking_date)
    ).order_by(
        extract('year', Bookings.booking_date).desc(),
        extract('month', Bookings.booking_date).desc()
    ).limit(12).all()

    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    result = []
    for i, row in enumerate(monthly_data):
        growth = 0
        if i < len(monthly_data) - 1:
            prev = monthly_data[i + 1]
            if prev.revenue > 0:
                growth = ((row.revenue - prev.revenue) / prev.revenue) * 100

        result.append({
            'month': f"{month_names[int(row.month)]} {int(row.year)}",
            'revenue': row.revenue or 0,
            'orders': row.orders or 0,
            'growth': round(growth, 2)
        })

    return jsonify({'monthly_sales': result})


@app.route('/api/admin/reports/daily-sales', methods=['GET'])
@require_admin
def get_daily_sales(user_id, role):
    """Get daily sales for last 7 days"""
    from sqlalchemy import func, extract

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    daily_data = db.session.query(
        func.date(Bookings.booking_date).label('date'),
        func.sum(Bookings.total_price).label('revenue'),
        func.count(Bookings.booking_id).label('orders')
    ).filter(
        Bookings.booking_date >= seven_days_ago
    ).group_by(
        func.date(Bookings.booking_date)
    ).order_by(
        func.date(Bookings.booking_date)
    ).all()

    result = [{
        'date': str(row.date),
        'revenue': row.revenue or 0,
        'orders': row.orders or 0
    } for row in daily_data]

    return jsonify({'daily_sales': result})


@app.route('/api/admin/reports/summary', methods=['GET'])
@require_admin
def get_sales_summary(user_id, role):
    """Get sales summary"""
    now = datetime.utcnow()
    first_of_month = datetime(now.year, now.month, 1)

    # This month
    revenue_this_month = db.session.query(db.func.sum(Bookings.total_price)).filter(
        Bookings.booking_date >= first_of_month
    ).scalar() or 0

    orders_this_month = Bookings.query.filter(
        Bookings.booking_date >= first_of_month
    ).count()

    # All time
    total_revenue = db.session.query(db.func.sum(Bookings.total_price)).scalar() or 0
    total_orders = Bookings.query.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return jsonify({
        'total_revenue_this_month': revenue_this_month,
        'total_orders_this_month': orders_this_month,
        'total_revenue_all_time': total_revenue,
        'avg_order_value': avg_order_value
    })


# =============================================================================
# FORECASTING ENDPOINT
# =============================================================================

@app.route('/api/admin/forecast/demand', methods=['GET'])
@require_admin
def get_demand_forecast(user_id, role):
    """Get demand forecast for a product"""
    product_id = request.args.get('product_id')
    months_ahead = int(request.args.get('months_ahead', 3))

    if not product_id:
        return jsonify({'message': 'product_id is required'}), 400

    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Simple moving average based forecast
    # In production, this would use more sophisticated algorithms
    avg_orders_per_month = product.num_orders / 3  # Assuming 3 months of data

    now = datetime.utcnow()
    forecast = []
    for i in range(1, months_ahead + 1):
        next_month = now + timedelta(days=30 * i)
        # Simple trend - slight increase
        predicted = int(avg_orders_per_month * (1 + (i * 0.1)))
        confidence = 'high' if i <= 1 else 'medium' if i <= 2 else 'low'

        forecast.append({
            'month': next_month.month,
            'year': next_month.year,
            'predicted_quantity': predicted,
            'confidence': confidence
        })

    return jsonify({
        'product_name': product.name,
        'method': 'Moving Average',
        'historical_data_points': product.num_orders,
        'forecast': forecast
    })


# =============================================================================
# DATABASE INITIALIZATION & SEED DATA
# =============================================================================

def init_db():
    """Initialize database with seed data"""
    with app.app_context():
        db.create_all()

        # Check if data already exists
        if Users.query.first() is None:
            print("Seeding database...")

            # Create admin user
            admin = Users(
                name='Admin User',
                email='admin@agriflow.com',
                password=hash_password('admin123'),
                mobile_no='9876543210',
                role='admin'
            )
            db.session.add(admin)

            # Create customer users
            customer1 = Users(
                name='John Farmer',
                email='john@farmer.com',
                password=hash_password('customer123'),
                mobile_no='9876543211',
                role='customer',
                user_orders=5
            )
            db.session.add(customer1)

            customer2 = Users(
                name='Jane Retailer',
                email='jane@retailer.com',
                password=hash_password('customer123'),
                mobile_no='9876543212',
                role='customer',
                user_orders=8
            )
            db.session.add(customer2)

            db.session.commit()

            # Create carts
            cart1 = Cart(user_id=customer1.user_id)
            cart2 = Cart(user_id=customer2.user_id)
            db.session.add_all([cart1, cart2])
            db.session.commit()

            # Create sample products
            products_data = [
                ('Urea (Nitrogen Fertilizer) - 50kg', 'High nitrogen content fertilizer for promoting healthy leaf growth. Suitable for all crops.', 350, 100, 15, 'Nitrogen Fertilizers'),
                ('DAP (Di-Ammonium Phosphate) - 50kg', 'Phosphate-rich fertilizer ideal for root development and flowering stage.', 1350, 50, 15, 'Phosphate Fertilizers'),
                ('Potash (Muriate of Potash) - 50kg', 'Potassium-rich fertilizer for improving crop quality and disease resistance.', 900, 200, 180, 'Potash Fertilizers'),
                ('NPK 10-26-26 - 50kg', 'Balanced fertilizer with nitrogen, phosphorus, and potassium for overall plant health.', 1200, 75, 60, 'NPK Fertilizers'),
                ('Vermicompost (Organic) - 25kg', '100% organic compost rich in micronutrients. Improves soil health naturally.', 450, 30, -5, 'Organic Fertilizers'),
                ('Neem Cake - 25kg', 'Organic pest repellent and soil enricher. Natural way to protect your crops.', 380, 80, 7, 'Organic Fertilizers'),
                ('NPK 19-19-19 - 50kg', 'Balanced water-soluble fertilizer for foliar application and drip irrigation.', 1450, 150, 90, 'NPK Fertilizers'),
                ('Calcium Nitrate - 25kg', 'Fast-acting calcium source for preventing blossom end rot in vegetables.', 680, 60, 45, 'Specialty Fertilizers'),
            ]

            for name, desc, price, qty, days_until_expiry, category in products_data:
                expiry = datetime.utcnow() + timedelta(days=days_until_expiry) if days_until_expiry > 0 else datetime.utcnow() - timedelta(days=abs(days_until_expiry))
                product = Products(
                    name=name,
                    description=desc,
                    price=price,
                    quantity=qty,
                    expiry_date=expiry,
                    category=category,
                    num_orders=0
                )
                db.session.add(product)

            db.session.commit()
            print("Database seeded successfully!")


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
