from flask import Blueprint, request, jsonify
from backend.models import db, User, Product, Review, Booking, BookingItem, Address, Cart, CartItem, Offer, OfferNotification, Notification
from datetime import datetime, timedelta
import pandas as pd

# Create blueprints
auth_bp = Blueprint('auth', __name__)
product_bp = Blueprint('product', __name__)
cart_bp = Blueprint('cart', __name__)
booking_bp = Blueprint('booking', __name__)
review_bp = Blueprint('review', __name__)
address_bp = Blueprint('address', __name__)

# Helper function to check if product is expired or expiring soon
def check_expiry_status(product):
    if product.expiry_date:
        now = datetime.utcnow()
        # Handle both string and datetime expiry_date
        expiry = product.expiry_date
        if isinstance(expiry, str):
            try:
                expiry = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
            except ValueError:
                expiry = datetime.strptime(expiry, '%Y-%m-%d')
        if expiry < now:
            product.expiry_status = 'expired'
        elif expiry < now + timedelta(days=3):  # Expiring within 3 days
            product.expiry_status = 'expiring_soon'
        else:
            product.expiry_status = 'valid'
    else:
        product.expiry_status = 'valid'
    return product.expiry_status

# Auth Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check for required fields
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],  # In production, hash the password
        mobile_no=data.get('mobile_no'),
        role=data.get('role', 'customer')
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Create a cart for the user
    cart = Cart(user_id=new_user.id)
    db.session.add(cart)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        user.last_login = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'role': user.role,
            'name': user.name
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

# Product Routes
@product_bp.route('/', methods=['GET'])
def get_products():
    # For customers, show only valid products (not expired)
    # For admins, show all products
    # We'll check role from request headers or token (simplified for now)
    # In a real app, you'd use authentication middleware
    role = request.headers.get('Role', 'customer')  # Simplified
    
    if role == 'admin':
        products = Product.query.all()
    else:
        products = Product.query.filter(Product.expiry_status != 'expired').all()
    
    output = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'quantity': product.quantity,
            'price': product.price,
            'date_added': product.date_added.isoformat() if product.date_added else None,
            'expiry_date': product.expiry_date.isoformat() if product.expiry_date else None,
            'expiry_status': product.expiry_status,
            'no_of_orders': product.no_of_orders
        }
        output.append(product_data)
    return jsonify({'products': output})

@product_bp.route('/', methods=['POST'])
def create_product():
    # Only admin can create products
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Convert expiry_date string to datetime object
    expiry_date = None
    if data.get('expiry_date'):
        try:
            expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
        except ValueError:
            try:
                expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'message': 'Invalid expiry_date format. Use YYYY-MM-DD'}), 400
    
    new_product = Product(
        name=data['name'],
        description=data.get('description'),
        quantity=data['quantity'],
        price=data['price'],
        expiry_date=expiry_date
    )
    # Check expiry status
    check_expiry_status(new_product)
    
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'product_id': new_product.id}), 201

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'quantity': product.quantity,
        'price': product.price,
        'date_added': product.date_added.isoformat() if product.date_added else None,
        'expiry_date': product.expiry_date.isoformat() if product.expiry_date else None,
        'expiry_status': product.expiry_status,
        'no_of_orders': product.no_of_orders
    }
    return jsonify({'product': product_data})

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.quantity = data.get('quantity', product.quantity)
    product.price = data.get('price', product.price)
    if 'expiry_date' in data:
        # Convert string to datetime object
        expiry_date_str = data['expiry_date']
        if expiry_date_str:
            try:
                product.expiry_date = datetime.fromisoformat(expiry_date_str)
            except ValueError:
                try:
                    product.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
                except ValueError:
                    pass  # Keep as None if invalid
        else:
            product.expiry_date = None
    
    check_expiry_status(product)
    
    db.session.commit()
    return jsonify({'message': 'Product updated'})

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    # Delete related booking items first
    from backend.models import BookingItem, CartItem, Review
    
    # Delete cart items referencing this product
    CartItem.query.filter_by(product_id=product_id).delete()
    
    # Delete booking items referencing this product
    BookingItem.query.filter_by(product_id=product_id).delete()
    
    # Delete reviews referencing this product
    Review.query.filter_by(product_id=product_id).delete()
    
    # Now delete the product
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

# Cart Routes
@cart_bp.route('/', methods=['GET'])
def get_cart():
    user_id = request.headers.get('User-ID')  # Simplified
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    
    output = []
    for item in cart.items:
        product = Product.query.get(item.product_id)
        item_data = {
            'cart_item_id': item.id,
            'product_id': product.id,
            'product_name': product.name,
            'quantity': item.quantity,
            'price': product.price,
            'total_price': product.price * item.quantity
        }
        output.append(item_data)
    
    total = sum(item['total_price'] for item in output)
    return jsonify({'cart_items': output, 'total_price': total})

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    data = request.get_json()
    product_id = data['product_id']
    quantity = data['quantity']
    
    product = Product.query.get_or_404(product_id)
    if product.quantity < quantity:
        return jsonify({'message': 'Insufficient stock'}), 400
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    
    # Check if product already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'message': 'Item added to cart'})

@cart_bp.route('/update/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    data = request.get_json()
    quantity = data['quantity']
    
    cart_item = CartItem.query.get_or_404(cart_item_id)
    # Verify cart belongs to user
    cart = Cart.query.filter_by(id=cart_item.cart_id, user_id=user_id).first()
    if not cart:
        return jsonify({'message': 'Unauthorized'}), 403
    
    product = Product.query.get(cart_item.product_id)
    if product.quantity < quantity:
        return jsonify({'message': 'Insufficient stock'}), 400
    
    cart_item.quantity = quantity
    db.session.commit()
    return jsonify({'message': 'Cart item updated'})

@cart_bp.route('/remove/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    cart_item = CartItem.query.get_or_404(cart_item_id)
    # Verify cart belongs to user
    cart = Cart.query.filter_by(id=cart_item.cart_id, user_id=user_id).first()
    if not cart:
        return jsonify({'message': 'Unauthorized'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'})

# Booking Routes
@booking_bp.route('/', methods=['POST'])
def create_booking():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    data = request.get_json()
    
    # Get user's cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        return jsonify({'message': 'Cart is empty'}), 400
    
    # Calculate total price
    total_price = 0
    booking_items_data = []
    for item in cart.items:
        product = Product.query.get(item.product_id)
        if product.quantity < item.quantity:
            return jsonify({'message': f'Insufficient stock for {product.name}'}), 400
        total_price += product.price * item.quantity
        booking_items_data.append({
            'product_id': product.id,
            'quantity': item.quantity,
            'price_at_purchase': product.price
        })
    
    # Convert delivery_date string to datetime object
    delivery_date = None
    if data.get('delivery_date'):
        try:
            delivery_date = datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00'))
        except ValueError:
            try:
                delivery_date = datetime.strptime(data['delivery_date'], '%Y-%m-%d')
            except ValueError:
                pass  # Keep as None if invalid
    
    # Create booking
    new_booking = Booking(
        user_id=user_id,
        total_price=total_price,
        delivery_address_id=data['delivery_address_id'],
        delivery_date=delivery_date,
        mode_of_payment=data['mode_of_payment']
    )
    db.session.add(new_booking)
    db.session.commit()  # To get the booking ID
    
    # Create booking items and update product quantities
    for item_data in booking_items_data:
        booking_item = BookingItem(
            booking_id=new_booking.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price_at_purchase=item_data['price_at_purchase']
        )
        db.session.add(booking_item)
        
        # Update product quantity
        product = Product.query.get(item_data['product_id'])
        product.quantity -= item_data['quantity']
        product.no_of_orders += item_data['quantity']
    
    # Update user's order count and total spent
    customer = User.query.get(user_id)
    if customer:
        customer.no_of_orders += 1
        customer.total_spent += total_price
    
    # Clear the cart
    CartItem.query.filter_by(cart_id=cart.id).delete()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Booking created successfully',
        'booking_id': new_booking.id,
        'total_price': total_price
    }), 201

@booking_bp.route('/history', methods=['GET'])
def get_booking_history():
    user_id = request.headers.get('User-ID')
    user_role = request.headers.get('Role')
    
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    # If admin, return all bookings from all customers
    if user_role == 'admin':
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    else:
        # Regular customers only see their own orders
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
    
    output = []
    for booking in bookings:
        # Get customer info
        customer = User.query.get(booking.user_id)
        customer_name = customer.name if customer else 'Unknown'
        
        # Get delivery address
        address = Address.query.get(booking.delivery_address_id)
        address_data = None
        if address:
            address_data = {
                'id': address.id,
                'address_line_1': address.address_line_1,
                'address_line_2': address.address_line_2,
                'city': address.city,
                'state': address.state,
                'pin_code': address.pin_code
            }
        
        # Get booking items
        items = []
        for item in booking.items:
            product = Product.query.get(item.product_id)
            item_data = {
                'product_id': product.id,
                'product_name': product.name if product else 'Unknown',
                'quantity': item.quantity,
                'price_at_purchase': item.price_at_purchase,
                'total_price': item.price_at_purchase * item.quantity
            }
            items.append(item_data)
        
        booking_data = {
            'id': booking.id,
            'user_id': booking.user_id,
            'customer_name': customer_name,
            'booking_date': booking.booking_date.isoformat(),
            'total_price': booking.total_price,
            'delivery_address': address_data,
            'delivery_date': booking.delivery_date.isoformat() if booking.delivery_date else None,
            'mode_of_payment': booking.mode_of_payment,
            'status': booking.status,
            'items': items
        }
        output.append(booking_data)
    
    return jsonify({'bookings': output})

# Review Routes
@review_bp.route('/', methods=['POST'])
def create_review():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    data = request.get_json()
    product_id = data['product_id']
    rating = data['rating']
    review_text = data.get('review', '')
    
    # Check if user has purchased this product (simplified: check if there's a booking with this product)
    # In a real app, you'd check the booking items for this user and product
    # For now, we'll allow any logged-in user to review (but note: user story says only after purchase)
    # We'll implement a simple check: if the user has at least one booking that includes this product
    has_purchased = False
    bookings = Booking.query.filter_by(user_id=user_id).all()
    for booking in bookings:
        for item in booking.items:
            if item.product_id == product_id:
                has_purchased = True
                break
        if has_purchased:
            break
    
    if not has_purchased:
        return jsonify({'message': 'You can only review products you have purchased'}), 403
    
    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_review:
        return jsonify({'message': 'You have already reviewed this product'}), 400
    
    new_review = Review(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        review=review_text
    )
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify({'message': 'Review created', 'review_id': new_review.id}), 201

@review_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).all()
    
    output = []
    for review in reviews:
        user = User.query.get(review.user_id)
        review_data = {
            'id': review.id,
            'user_name': user.name if user else 'Unknown',
            'rating': review.rating,
            'review': review.review,
            'created_at': review.created_at.isoformat()
        }
        output.append(review_data)
    
    return jsonify({'reviews': output})

# Address Routes
@address_bp.route('/', methods=['GET'])
def get_addresses():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    addresses = Address.query.filter_by(user_id=user_id).all()
    
    output = []
    for address in addresses:
        address_data = {
            'id': address.id,
            'address_line_1': address.address_line_1,
            'address_line_2': address.address_line_2,
            'city': address.city,
            'state': address.state,
            'pin_code': address.pin_code,
            'is_default': address.is_default
        }
        output.append(address_data)
    
    return jsonify({'addresses': output})

@address_bp.route('/', methods=['POST'])
def create_address():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    data = request.get_json()
    
    # If this is set as default, unset other defaults for this user
    if data.get('is_default'):
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    new_address = Address(
        user_id=user_id,
        address_line_1=data['address_line_1'],
        address_line_2=data.get('address_line_2'),
        city=data['city'],
        state=data['state'],
        pin_code=data['pin_code'],
        is_default=data.get('is_default', False)
    )
    db.session.add(new_address)
    db.session.commit()
    
    return jsonify({'message': 'Address created', 'address_id': new_address.id}), 201

@address_bp.route('/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    address = Address.query.get_or_404(address_id)
    if address.user_id != int(user_id):
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # If setting as default, unset other defaults
    if data.get('is_default'):
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    address.address_line_1 = data.get('address_line_1', address.address_line_1)
    address.address_line_2 = data.get('address_line_2', address.address_line_2)
    address.city = data.get('city', address.city)
    address.state = data.get('state', address.state)
    address.pin_code = data.get('pin_code', address.pin_code)
    address.is_default = data.get('is_default', address.is_default)
    
    db.session.commit()
    return jsonify({'message': 'Address updated'})

@address_bp.route('/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    address = Address.query.get_or_404(address_id)
    if address.user_id != int(user_id):
        return jsonify({'message': 'Unauthorized'}), 403
    
    db.session.delete(address)
    db.session.commit()
    return jsonify({'message': 'Address deleted'})

# Admin Routes (for dashboard, notifications, etc.)
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
def admin_dashboard_stats():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get stats for admin dashboard
    total_products = Product.query.count()
    total_users = User.query.count()
    total_orders = Booking.query.count()
    
    # Expiring soon products (within 3 days)
    soon = datetime.utcnow() + timedelta(days=3)
    expiring_soon = Product.query.filter(
        Product.expiry_date <= soon,
        Product.expiry_date >= datetime.utcnow(),
        Product.expiry_status != 'expired'
    ).count()
    
    expired_products = Product.query.filter_by(expiry_status='expired').count()
    
    # Low stock products (quantity < 10)
    low_stock = Product.query.filter(Product.quantity < 10).count()
    
    return jsonify({
        'total_products': total_products,
        'total_users': total_users,
        'total_orders': total_orders,
        'expiring_soon': expiring_soon,
        'expired_products': expired_products,
        'low_stock': low_stock
    })

@admin_bp.route('/products/expiring', methods=['GET'])
def get_expiring_products():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get products expiring within 3 days
    soon = datetime.utcnow() + timedelta(days=3)
    products = Product.query.filter(
        Product.expiry_date <= soon,
        Product.expiry_date >= datetime.utcnow()
    ).all()
    
    output = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'quantity': product.quantity,
            'expiry_date': product.expiry_date.isoformat(),
            'days_until_expiry': (product.expiry_date - datetime.utcnow()).days
        }
        output.append(product_data)
    
    return jsonify({'expiring_products': output})

@admin_bp.route('/products/expired', methods=['GET'])
def get_expired_products():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    products = Product.query.filter_by(expiry_status='expired').all()
    
    output = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'quantity': product.quantity,
            'expiry_date': product.expiry_date.isoformat() if product.expiry_date else None
        }
        output.append(product_data)
    
    return jsonify({'expired_products': output})

@admin_bp.route('/customers/top', methods=['GET'])
def get_top_customers():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get top customers by number of orders - using actual booking counts
    # First get all users who have at least one booking
    from sqlalchemy import func
    
    # Get user IDs with their order counts from bookings table
    customer_orders = db.session.query(
        Booking.user_id,
        func.count(Booking.id).label('order_count'),
        func.sum(Booking.total_price).label('total_spent')
    ).group_by(Booking.user_id).order_by(func.count(Booking.id).desc()).limit(10).all()
    
    output = []
    for user_id, order_count, total_spent in customer_orders:
        user = User.query.get(user_id)
        if user:
            customer_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'no_of_orders': order_count,
                'total_spent': float(total_spent) if total_spent else 0
            }
            output.append(customer_data)
    
    return jsonify({'top_customers': output})

# Automated Monthly Reports
@admin_bp.route('/reports/monthly', methods=['GET'])
def get_monthly_report():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get month and year from query params, default to current month
    month = request.args.get('month', datetime.utcnow().month, type=int)
    year = request.args.get('year', datetime.utcnow().year, type=int)
    
    # Validate month and year
    if month < 1 or month > 12:
        return jsonify({'message': 'Invalid month'}), 400
    if year < 2020:  # Reasonable minimum year
        return jsonify({'message': 'Invalid year'}), 400
    
    # Calculate start and end dates for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get bookings for the month
    bookings = Booking.query.filter(
        Booking.booking_date >= start_date,
        Booking.booking_date < end_date
    ).all()
    
    # Calculate statistics
    total_sales = sum(booking.total_price for booking in bookings)
    total_orders = len(bookings)
    
    # Group by product to get sales per product
    product_sales = {}
    for booking in bookings:
        for item in booking.items:
            product_id = item.product_id
            if product_id not in product_sales:
                product = Product.query.get(product_id)
                product_sales[product_id] = {
                    'product_id': product_id,
                    'product_name': product.name,
                    'quantity_sold': 0,
                    'total_revenue': 0
                }
            product_sales[product_id]['quantity_sold'] += item.quantity
            product_sales[product_id]['total_revenue'] += item.quantity * item.price_at_purchase
    
    # Sort products by revenue
    sorted_products = sorted(product_sales.values(), key=lambda x: x['total_revenue'], reverse=True)
    
    # Get customer statistics
    customer_spending = {}
    for booking in bookings:
        user_id = booking.user_id
        if user_id not in customer_spending:
            user = User.query.get(user_id)
            customer_spending[user_id] = {
                'user_id': user_id,
                'customer_name': user.name if user else 'Unknown',
                'customer_email': user.email if user else 'Unknown',
                'total_spent': 0,
                'order_count': 0
            }
        customer_spending[user_id]['total_spent'] += booking.total_price
        customer_spending[user_id]['order_count'] += 1
    
    # Sort customers by spending
    top_customers = sorted(customer_spending.values(), key=lambda x: x['total_spent'], reverse=True)[:10]
    
    # Payment method breakdown
    payment_breakdown = {}
    for booking in bookings:
        method = booking.mode_of_payment
        if method not in payment_breakdown:
            payment_breakdown[method] = 0
        payment_breakdown[method] += booking.total_price
    
    # Status breakdown
    status_breakdown = {}
    for booking in bookings:
        status = booking.status
        if status not in status_breakdown:
            status_breakdown[status] = 0
        status_breakdown[status] += 1
    
    return jsonify({
        'month': month,
        'year': year,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'product_sales': sorted_products,
        'top_customers': top_customers,
        'payment_breakdown': payment_breakdown,
        'status_breakdown': status_breakdown
    })

# Demand Forecasting (ML Integration)
@admin_bp.route('/forecast/demand', methods=['GET'])
def forecast_demand():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get product ID and forecast period from query params
    product_id = request.args.get('product_id', type=int)
    months_ahead = request.args.get('months_ahead', 3, type=int)  # Default to 3 months
    
    # Validate inputs
    if product_id is None:
        return jsonify({'message': 'Product ID is required'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    if months_ahead < 1 or months_ahead > 12:
        return jsonify({'message': 'Forecast period must be between 1 and 12 months'}), 400
    
    # Get historical sales data (last 24 months)
    end_date = datetime.utcnow()
    start_date = datetime(end_date.year - 2, end_date.month, 1)  # Approximately 2 years ago
    
    # Get all bookings in the historical period
    historical_bookings = Booking.query.filter(
        Booking.booking_date >= start_date,
        Booking.booking_date <= end_date
    ).all()
    
    # Extract monthly sales for the specific product
    monthly_sales = {}  # {year_month: quantity}
    
    for booking in historical_bookings:
        for item in booking.items:
            if item.product_id == product_id:
                year_month = booking.booking_date.strftime('%Y-%m')
                if year_month not in monthly_sales:
                    monthly_sales[year_month] = 0
                monthly_sales[year_month] += item.quantity
    
    # Convert to sorted list of (date, quantity) tuples
    sorted_months = sorted(monthly_sales.items())
    
    # If we don't have enough data, use simple average
    if len(sorted_months) < 3:
        # Calculate average monthly sales from available data
        if sorted_months:
            avg_sales = sum(quantity for _, quantity in sorted_months) / len(sorted_months)
        else:
            # No historical data, use a default based on current stock or other factors
            avg_sales = max(1, product.quantity // 12)  # Assume we want to sell current stock over a year
        
        # Generate forecast
        forecast_data = []
        current_date = end_date
        for i in range(months_ahead):
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
            
            forecast_data.append({
                'month': current_date.month,
                'year': current_date.year,
                'predicted_quantity': round(avg_sales),
                'confidence': 'low'  # Low confidence due to limited data
            })
        
        return jsonify({
            'product_id': product_id,
            'product_name': product.name,
            'forecast_period_months': months_ahead,
            'historical_data_points': len(sorted_months),
            'forecast': forecast_data,
            'method': 'average_based_due_to_limited_data'
        })
    
    # Simple linear regression forecast for demonstration
    # In a real implementation, you would use proper ML models
    quantities = [quantity for _, quantity in sorted_months]
    
    # Calculate simple trend (month-over-month growth)
    if len(quantities) >= 2:
        # Calculate average month-over-month change
        changes = []
        for i in range(1, len(quantities)):
            if quantities[i-1] != 0:  # Avoid division by zero
                change = (quantities[i] - quantities[i-1]) / quantities[i-1]
                changes.append(change)
        
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # Apply trend to forecast
        last_quantity = quantities[-1]
        forecast_data = []
        current_date = end_date
        
        for i in range(months_ahead):
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
            
            # Apply trend with damping (reduce effect over time)
            damping_factor = 1 - (i * 0.1)  # Reduce trend effect by 10% each month
            predicted_quantity = last_quantity * (1 + avg_change * damping_factor)
            predicted_quantity = max(0, round(predicted_quantity))  # Ensure non-negative
            
            forecast_data.append({
                'month': current_date.month,
                'year': current_date.year,
                'predicted_quantity': predicted_quantity,
                'confidence': 'medium' if i < 3 else 'low'  # Confidence decreases over time
            })
            
            # Update last_quantity for next iteration
            last_quantity = predicted_quantity
    else:
        # Fallback to average if we can't calculate trend
        avg_sales = sum(quantities) / len(quantities)
        forecast_data = []
        current_date = end_date
        
        for i in range(months_ahead):
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
            
            forecast_data.append({
                'month': current_date.month,
                'year': current_date.year,
                'predicted_quantity': round(avg_sales),
                'confidence': 'low'
            })
    
    return jsonify({
        'product_id': product_id,
        'product_name': product.name,
        'forecast_period_months': months_ahead,
        'historical_data_points': len(sorted_months),
        'forecast': forecast_data,
        'method': 'simple_linear_trend'
    })

# Intelligent Recommendation System
@admin_bp.route('/recommendations/push-expiry', methods=['GET'])
def recommend_push_expiry():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get products that are expiring soon (within 7 days) and have sufficient stock
    soon = datetime.utcnow() + timedelta(days=7)
    expiring_products = Product.query.filter(
        Product.expiry_date <= soon,
        Product.expiry_date >= datetime.utcnow(),
        Product.quantity > 0
    ).order_by(Product.expiry_date.asc()).all()
    
    output = []
    for product in expiring_products:
        days_until_expiry = (product.expiry_date - datetime.utcnow()).days
        urgency = 'high' if days_until_expiry <= 3 else 'medium' if days_until_expiry <= 5 else 'low'
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'quantity': product.quantity,
            'expiry_date': product.expiry_date.isoformat(),
            'days_until_expiry': days_until_expiry,
            'urgency': urgency,
            'recommended_action': f'Push sale of {product.name} - expires in {days_until_expiry} days'
        }
        output.append(product_data)
    
    return jsonify({'expiry_recommendations': output})

@admin_bp.route('/recommendations/high-demand', methods=['GET'])
def recommend_high_demand():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get products with high demand based on recent sales (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Query to get products sold in last 30 days, ordered by quantity sold
    from sqlalchemy import func
    
    high_demand_products = db.session.query(
        Product.id,
        Product.name,
        Product.quantity,
        func.sum(BookingItem.quantity).label('units_sold')
    ).join(BookingItem, BookingItem.product_id == Product.id)\
     .join(Booking, BookingItem.booking_id == Booking.id)\
     .filter(Booking.booking_date >= thirty_days_ago)\
     .group_by(Product.id, Product.name, Product.quantity)\
     .order_by(func.sum(BookingItem.quantity).desc())\
     .limit(10)\
     .all()
    
    output = []
    for product in high_demand_products:
        # Calculate demand level based on units sold
        units_sold = product.units_sold
        if units_sold >= 50:
            demand_level = 'high'
        elif units_sold >= 20:
            demand_level = 'medium'
        else:
            demand_level = 'low'
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'current_stock': product.quantity,
            'units_sold_last_30_days': units_sold,
            'demand_level': demand_level,
            'recommended_action': f'Increase stock of {product.name} - high demand product'
        }
        output.append(product_data)
    
    return jsonify({'high_demand_recommendations': output})

# Customer Credit Score Dashboard
@admin_bp.route('/customers/credit-scores', methods=['GET'])
def get_customer_credit_scores():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Update total_spent for all customers from their existing bookings
    customers = User.query.filter_by(role='customer').all()
    for customer in customers:
        from backend.models import Booking
        bookings = Booking.query.filter_by(user_id=customer.id).all()
        total = sum(booking.total_price for booking in bookings)
        if customer.total_spent != total:
            customer.total_spent = total
    db.session.commit()
    
    # Get all customers with their credit scores and details
    customers = User.query.filter_by(role='customer').order_by(User.credit_score.desc()).all()
    
    output = []
    for customer in customers:
        # Calculate outstanding balance
        total_spent = customer.total_spent
        total_paid = customer.total_paid
        outstanding_balance = max(0, total_spent - total_paid)
        
        customer_data = {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'mobile_no': customer.mobile_no,
            'credit_score': customer.credit_score,
            'total_orders': customer.no_of_orders,
            'total_spent': total_spent,
            'total_paid': total_paid,
            'outstanding_balance': outstanding_balance,
            'last_login': customer.last_login.isoformat() if customer.last_login else None
        }
        output.append(customer_data)
    
    return jsonify({'customers': output})

@admin_bp.route('/customers/<int:customer_id>/credit-score', methods=['PUT'])
def update_customer_credit_score(customer_id):
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    customer = User.query.get_or_404(customer_id)
    if customer.role != 'customer':
        return jsonify({'message': 'Invalid customer'}), 400
    
    data = request.get_json()
    new_score = data.get('credit_score')
    
    if new_score is None or not (0 <= new_score <= 100):
        return jsonify({'message': 'Credit score must be between 0 and 100'}), 400
    
    customer.credit_score = new_score
    db.session.commit()
    
    return jsonify({'message': 'Credit score updated successfully'})

# Pending Payment Tracking
@admin_bp.route('/payments/pending', methods=['GET'])
def get_pending_payments():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get all bookings with status pending or confirmed (not delivered/cancelled)
    # that have outstanding payments (mode of payment is Credit)
    pending_bookings = Booking.query.filter(
        Booking.mode_of_payment == 'Credit',
        Booking.status.in_(['pending', 'confirmed'])
    ).all()
    
    output = []
    for booking in pending_bookings:
        user = User.query.get(booking.user_id)
        if not user:
            continue
            
        # Calculate outstanding amount (for simplicity, we'll assume full amount is pending)
        # In a real system, you might have partial payments
        outstanding_amount = booking.total_price
        
        booking_data = {
            'id': booking.id,
            'booking_date': booking.booking_date.isoformat(),
            'total_price': booking.total_price,
            'outstanding_amount': outstanding_amount,
            'customer': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'mobile_no': user.mobile_no
            },
            'delivery_date': booking.delivery_date.isoformat() if booking.delivery_date else None,
            'status': booking.status
        }
        output.append(booking_data)
    
    # Sort by outstanding amount (highest first)
    output.sort(key=lambda x: x['outstanding_amount'], reverse=True)
    
    return jsonify({'pending_payments': output})

@admin_bp.route('/payments/record', methods=['POST'])
def record_payment():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    booking_id = data.get('booking_id')
    amount_paid = data.get('amount_paid')
    
    if not booking_id or amount_paid is None:
        return jsonify({'message': 'Booking ID and amount paid are required'}), 400
    
    try:
        amount_paid = float(amount_paid)
        if amount_paid <= 0:
            return jsonify({'message': 'Amount paid must be positive'}), 400
    except ValueError:
        return jsonify({'message': 'Invalid amount paid'}), 400
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.mode_of_payment != 'Credit':
        return jsonify({'message': 'Payment recording is only for credit purchases'}), 400
    
    # Update customer's total paid
    customer = User.query.get(booking.user_id)
    if customer:
        customer.total_paid += amount_paid
        # Update credit score based on payment history (simple implementation)
        # In a real system, this would be more sophisticated
        if customer.total_spent > 0:
            payment_ratio = customer.total_paid / customer.total_spent
            # Increase credit score for good payment ratio, decrease for poor
            if payment_ratio >= 0.9:
                customer.credit_score = min(100, customer.credit_score + 1)
            elif payment_ratio < 0.5:
                customer.credit_score = max(0, customer.credit_score - 1)
    
    # If full payment received, update booking status
    if amount_paid >= booking.total_price:
        booking.status = 'confirmed'  # Or you might have a 'paid' status
    
    db.session.commit()
    
    return jsonify({'message': 'Payment recorded successfully'})
@admin_bp.route('/customers/top-by-spending', methods=['GET'])
def get_top_customers_by_spending():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get top customers by total spent
    top_customers = User.query.filter_by(role='customer').order_by(User.total_spent.desc()).limit(10).all()
    
    output = []
    for customer in top_customers:
        customer_data = {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'total_spent': customer.total_spent,
            'total_orders': customer.no_of_orders
        }
        output.append(customer_data)
    
    return jsonify({'top_customers_by_spending': output})

# Offer & Discount Notifications
@admin_bp.route('/offers', methods=['GET'])
def get_offers():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    offers = Offer.query.all()
    
    output = []
    for offer in offers:
        offer_data = {
            'id': offer.id,
            'title': offer.title,
            'description': offer.description,
            'discount_type': offer.discount_type,
            'discount_value': offer.discount_value,
            'product_id': offer.product_id,
            'product_name': offer.product.name if offer.product else 'All Products',
            'start_date': offer.start_date.isoformat(),
            'end_date': offer.end_date.isoformat(),
            'is_active': offer.is_active,
            'usage_limit': offer.usage_limit,
            'times_used': offer.times_used,
            'created_at': offer.created_at.isoformat()
        }
        output.append(offer_data)
    
    return jsonify({'offers': output})

@admin_bp.route('/offers', methods=['POST'])
def create_offer():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'discount_type', 'discount_value', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Validate discount type
    if data['discount_type'] not in ['percentage', 'fixed']:
        return jsonify({'message': 'Discount type must be percentage or fixed'}), 400
    
    # Validate discount value
    try:
        discount_value = float(data['discount_value'])
        if data['discount_type'] == 'percentage' and (discount_value < 0 or discount_value > 100):
            return jsonify({'message': 'Percentage discount must be between 0 and 100'}), 400
        if data['discount_type'] == 'fixed' and discount_value < 0:
            return jsonify({'message': 'Fixed discount must be positive'}), 400
    except ValueError:
        return jsonify({'message': 'Invalid discount value'}), 400
    
    # Parse dates
    try:
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400
    
    if start_date >= end_date:
        return jsonify({'message': 'Start date must be before end date'}), 400
    
    # Validate product_id if provided
    product_id = data.get('product_id')
    if product_id is not None:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 400
    
    new_offer = Offer(
        title=data['title'],
        description=data.get('description', ''),
        discount_type=data['discount_type'],
        discount_value=discount_value,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        is_active=data.get('is_active', True),
        usage_limit=data.get('usage_limit')
    )
    
    db.session.add(new_offer)
    db.session.commit()
    
    return jsonify({'message': 'Offer created successfully', 'offer_id': new_offer.id}), 201

@admin_bp.route('/offers/<int:offer_id>', methods=['PUT'])
def update_offer(offer_id):
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    offer = Offer.query.get_or_404(offer_id)
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        offer.title = data['title']
    if 'description' in data:
        offer.description = data['description']
    if 'discount_type' in data:
        if data['discount_type'] not in ['percentage', 'fixed']:
            return jsonify({'message': 'Discount type must be percentage or fixed'}), 400
        offer.discount_type = data['discount_type']
    if 'discount_value' in data:
        try:
            discount_value = float(data['discount_value'])
            if offer.discount_type == 'percentage' and (discount_value < 0 or discount_value > 100):
                return jsonify({'message': 'Percentage discount must be between 0 and 100'}), 400
            if offer.discount_type == 'fixed' and discount_value < 0:
                return jsonify({'message': 'Fixed discount must be positive'}), 400
            offer.discount_value = discount_value
        except ValueError:
            return jsonify({'message': 'Invalid discount value'}), 400
    if 'start_date' in data:
        try:
            offer.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid start date format'}), 400
    if 'end_date' in data:
        try:
            offer.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid end date format'}), 400
    if 'is_active' in data:
        offer.is_active = data['is_active']
    if 'usage_limit' in data:
        offer.usage_limit = data['usage_limit']
    if 'product_id' in data:
        product_id = data['product_id']
        if product_id is not None:
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'message': 'Product not found'}), 400
        offer.product_id = product_id
    
    # Validate date order
    if offer.start_date >= offer.end_date:
        return jsonify({'message': 'Start date must be before end date'}), 400
    
    db.session.commit()
    
    return jsonify({'message': 'Offer updated successfully'})

@admin_bp.route('/offers/<int:offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    
    return jsonify({'message': 'Offer deleted successfully'})

@admin_bp.route('/offers/send-notifications', methods=['POST'])
def send_offer_notifications():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    offer_id = data.get('offer_id')
    
    if not offer_id:
        return jsonify({'message': 'Offer ID is required'}), 400
    
    offer = Offer.query.get(offer_id)
    if not offer:
        return jsonify({'message': 'Offer not found'}), 404
    
    if not offer.is_active:
        return jsonify({'message': 'Offer is not active'}), 400
    
    # Check if offer is within valid date range
    now = datetime.utcnow()
    if now < offer.start_date or now > offer.end_date:
        return jsonify({'message': 'Offer is not currently active'}), 400
    
    # Check usage limit
    if offer.usage_limit is not None and offer.times_used >= offer.usage_limit:
        return jsonify({'message': 'Offer usage limit has been reached'}), 400
    
    # Get target customers
    # For simplicity, we'll send to all customers
    # In a real system, you might target based on purchase history, location, etc.
    customers = User.query.filter_by(role='customer').all()
    
    notifications_sent = 0
    for customer in customers:
        # Check if customer already has a notification for this offer
        existing_notification = OfferNotification.query.filter_by(
            offer_id=offer.id,
            user_id=customer.id
        ).first()
        
        if not existing_notification:
            # Create offer notification
            offer_notification = OfferNotification(
                offer_id=offer.id,
                user_id=customer.id
            )
            db.session.add(offer_notification)
            
            # Create user notification
            notification = Notification(
                user_id=customer.id,
                title=f"Special Offer: {offer.title}",
                message=f"Get {offer.discount_value}{'%' if offer.discount_type == 'percentage' else '₹'} off on {offer.product.name if offer.product else 'all products'}!",
                offer_id=offer.id
            )
            db.session.add(notification)
            
            notifications_sent += 1
    
    # Update offer usage (in a real system, this would happen when the offer is actually used)
    # For now, we'll just increment times_used by the number of notifications sent
    offer.times_used += notifications_sent
    
    db.session.commit()
    
    return jsonify({
        'message': f'Offer notifications sent to {notifications_sent} customers',
        'notifications_sent': notifications_sent
    })

@booking_bp.route('/notifications/offers', methods=['GET'])
def get_offer_notifications():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    # Get offer notifications for the user
    offer_notifications = db.session.query(OfferNotification).filter_by(
        user_id=user_id
    ).join(Offer).filter(
        Offer.is_active == True,
        Offer.start_date <= datetime.utcnow(),
        Offer.end_date >= datetime.utcnow()
    ).all()
    
    output = []
    for on in offer_notifications:
        offer_data = {
            'id': on.offer.id,
            'title': on.offer.title,
            'description': on.offer.description,
            'discount_type': on.offer.discount_type,
            'discount_value': on.offer.discount_value,
            'product_name': on.offer.product.name if on.offer.product else 'All Products'
        }
        
        notification_data = {
            'id': on.id,
            'offer': offer_data,
            'is_sent': on.is_sent,
            'sent_at': on.sent_at.isoformat() if on.sent_at else None,
            'is_read': on.is_read,
            'read_at': on.read_at.isoformat() if on.read_at else None,
            'created_at': on.created_at.isoformat()
        }
        output.append(notification_data)
    
    return jsonify({'offer_notifications': output})

@booking_bp.route('/notifications/offers/<int:notification_id>/read', methods=['PUT'])
def mark_offer_notification_as_read(notification_id):
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    notification = OfferNotification.query.get_or_404(notification_id)
    if notification.user_id != int(user_id):
        return jsonify({'message': 'Unauthorized'}), 403
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Offer notification marked as read'})

# Review Monitoring & Analysis (Admin)
@admin_bp.route('/reviews', methods=['GET'])
def get_all_reviews():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get all reviews with pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    reviews = Review.query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    output = []
    for review in reviews.items:
        user = User.query.get(review.user_id)
        product = Product.query.get(review.product_id)
        review_data = {
            'id': review.id,
            'product_id': review.product_id,
            'product_name': product.name if product else 'Unknown',
            'user_id': review.user_id,
            'user_name': user.name if user else 'Unknown',
            'rating': review.rating,
            'review': review.review,
            'created_at': review.created_at.isoformat()
        }
        output.append(review_data)
    
    return jsonify({
        'reviews': output,
        'total': reviews.total,
        'pages': reviews.pages,
        'current_page': page
    })

@admin_bp.route('/reviews/product/<int:product_id>', methods=['GET'])
def get_product_reviews_for_analysis(product_id):
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    
    # Calculate review statistics
    total_reviews = len(reviews)
    if total_reviews > 0:
        avg_rating = sum(review.rating for review in reviews) / total_reviews
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        # Convert to percentages
        rating_distribution_pct = {
            k: round((v / total_reviews) * 100, 2) for k, v in rating_distribution.items()
        }
    else:
        avg_rating = 0
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        rating_distribution_pct = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
    
    output = []
    for review in reviews:
        user = User.query.get(review.user_id)
        review_data = {
            'id': review.id,
            'user_id': review.user_id,
            'user_name': user.name if user else 'Unknown',
            'rating': review.rating,
            'review': review.review,
            'created_at': review.created_at.isoformat()
        }
        output.append(review_data)
    
    return jsonify({
        'product_id': product_id,
        'product_name': product.name,
        'total_reviews': total_reviews,
        'average_rating': round(avg_rating, 2),
        'rating_distribution': rating_distribution,
        'rating_distribution_percentage': rating_distribution_pct,
        'reviews': output
    })

@admin_bp.route('/reviews/summary', methods=['GET'])
def get_reviews_summary():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get overall review statistics
    total_reviews = Review.query.count()
    
    if total_reviews > 0:
        avg_rating = db.session.query(db.func.avg(Review.rating)).scalar()
        rating_distribution = db.session.query(
            Review.rating, db.func.count(Review.id)
        ).group_by(Review.rating).all()
        
        rating_dist_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating, count in rating_distribution:
            rating_dist_dict[rating] = count
        
        rating_dist_pct = {
            k: round((v / total_reviews) * 100, 2) for k, v in rating_dist_dict.items()
        }
    else:
        avg_rating = 0
        rating_dist_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        rating_dist_pct = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
    
    # Get top rated products
    top_rated_products = db.session.query(
        Product.id,
        Product.name,
        db.func.avg(Review.rating).label('avg_rating'),
        db.func.count(Review.id).label('review_count')
    ).join(Review, Review.product_id == Product.id)\
     .group_by(Product.id, Product.name)\
     .having(db.func.count(Review.id) >= 3)\
     .order_by(db.func.avg(Review.rating).desc())\
     .limit(10)\
     .all()
    
    top_rated = []
    for product in top_rated_products:
        top_rated.append({
            'product_id': product.id,
            'product_name': product.name,
            'average_rating': round(product.avg_rating, 2),
            'review_count': product.review_count
        })
    
    # Get most reviewed products
    most_reviewed_products = db.session.query(
        Product.id,
        Product.name,
        db.func.count(Review.id).label('review_count'),
        db.func.avg(Review.rating).label('avg_rating')
    ).join(Review, Review.product_id == Product.id)\
     .group_by(Product.id, Product.name)\
     .order_by(db.func.count(Review.id).desc())\
     .limit(10)\
     .all()
    
    most_reviewed = []
    for product in most_reviewed_products:
        most_reviewed.append({
            'product_id': product.id,
            'product_name': product.name,
            'review_count': product.review_count,
            'average_rating': round(product.avg_rating, 2)
        })
    
    return jsonify({
        'total_reviews': total_reviews,
        'average_rating': round(avg_rating, 2) if avg_rating else 0,
        'rating_distribution': rating_dist_dict,
        'rating_distribution_percentage': rating_dist_pct,
        'top_rated_products': top_rated,
        'most_reviewed_products': most_reviewed
    })

# Real-time Purchase Notifications
@booking_bp.route('/notifications', methods=['POST'])
def create_notification():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    data = request.get_json()
    title = data.get('title')
    message = data.get('message')
    booking_id = data.get('booking_id')  # Optional
    
    if not title or not message:
        return jsonify({'message': 'Title and message are required'}), 400
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Verify booking exists if provided
    if booking_id:
        booking = Booking.query.get(booking_id)
        if not booking or booking.user_id != user_id:
            return jsonify({'message': 'Invalid booking'}), 400
    
    new_notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        booking_id=booking_id
    )
    db.session.add(new_notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification created', 'notification_id': new_notification.id}), 201

@booking_bp.route('/notifications', methods=['GET'])
def get_notifications():
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    # Get unread notifications by default, or all if specified
    unread_only = request.args.get('unread_only', 'true').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    output = []
    for notification in notifications:
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'booking_id': notification.booking_id
        }
        output.append(notification_data)
    
    return jsonify({'notifications': output})

@booking_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_as_read(notification_id):
    user_id = request.headers.get('User-ID')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != int(user_id):
        return jsonify({'message': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'})

# Manual Sales Entry
@admin_bp.route('/sales/manual', methods=['POST'])
def manual_sales_entry():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['user_id', 'delivery_address_id', 'mode_of_payment', 'items']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    user_id = data['user_id']
    delivery_address_id = data['delivery_address_id']
    mode_of_payment = data['mode_of_payment']
    delivery_date = data.get('delivery_date')
    items = data['items']  # List of {product_id, quantity}
    
    # Verify user exists and is customer
    user = User.query.get(user_id)
    if not user or user.role != 'customer':
        return jsonify({'message': 'Invalid customer'}), 400
    
    # Verify address exists
    address = Address.query.get(delivery_address_id)
    if not address or address.user_id != user_id:
        return jsonify({'message': 'Invalid delivery address'}), 400
    
    # Calculate total price and validate stock
    total_price = 0
    booking_items_data = []
    
    for item in items:
        product_id = item['product_id']
        quantity = item['quantity']
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': f'Product not found: {product_id}'}), 400
        
        if product.quantity < quantity:
            return jsonify({'message': f'Insufficient stock for {product.name}'}), 400
        
        total_price += product.price * quantity
        booking_items_data.append({
            'product_id': product_id,
            'quantity': quantity,
            'price_at_purchase': product.price
        })
    
    # Create booking
    new_booking = Booking(
        user_id=user_id,
        total_price=total_price,
        delivery_address_id=delivery_address_id,
        delivery_date=delivery_date,
        mode_of_payment=mode_of_payment
    )
    db.session.add(new_booking)
    db.session.commit()  # To get the booking ID
    
    # Create booking items and update product quantities
    for item_data in booking_items_data:
        booking_item = BookingItem(
            booking_id=new_booking.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price_at_purchase=item_data['price_at_purchase']
        )
        db.session.add(booking_item)
        
        # Update product quantity and order count
        product = Product.query.get(item_data['product_id'])
        product.quantity -= item_data['quantity']
        product.no_of_orders += item_data['quantity']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Sales entry created successfully',
        'booking_id': new_booking.id,
        'total_price': total_price
    }), 201

# Excel Upload for Sales
@admin_bp.route('/sales/upload-excel', methods=['POST'])
def upload_excel_sales():
    if request.headers.get('Role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xls'):
        return jsonify({'message': 'Only Excel files are allowed'}), 400
    
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Expected columns: customer_email, product_name, quantity, delivery_address_id, mode_of_payment, delivery_date (optional)
        required_columns = ['customer_email', 'product_name', 'quantity', 'delivery_address_id', 'mode_of_payment']
        for col in required_columns:
            if col not in df.columns:
                return jsonify({'message': f'Missing required column: {col}'}), 400
        
        successful_entries = 0
        failed_entries = []
        
        for index, row in df.iterrows():
            try:
                # Find customer by email
                customer = User.query.filter_by(email=row['customer_email'], role='customer').first()
                if not customer:
                    failed_entries.append({
                        'row': int(index) + 2,  # +2 for header and 0-based index
                        'error': 'Customer not found'
                    })
                    continue
                
                # Find product by name
                product = Product.query.filter_by(name=row['product_name']).first()
                if not product:
                    failed_entries.append({
                        'row': int(index) + 2,
                        'error': 'Product not found'
                    })
                    continue
                
                # Validate quantity
                try:
                    quantity = int(row['quantity'])
                    if quantity <= 0:
                        raise ValueError
                except (ValueError, TypeError):
                    failed_entries.append({
                        'row': int(index) + 2,
                        'error': 'Invalid quantity'
                    })
                    continue
                
                # Check stock
                if product.quantity < quantity:
                    failed_entries.append({
                        'row': int(index) + 2,
                        'error': f'Insufficient stock for {product.name}'
                    })
                    continue
                
                # Validate delivery address
                try:
                    address_id = int(row['delivery_address_id'])
                    address = Address.query.get(address_id)
                    if not address or address.user_id != customer.id:
                        failed_entries.append({
                            'row': int(index) + 2,
                            'error': 'Invalid delivery address'
                        })
                        continue
                except (ValueError, TypeError):
                    failed_entries.append({
                        'row': int(index) + 2,
                        'error': 'Invalid delivery address ID'
                    })
                    continue
                
                # Validate mode of payment
                mode_of_payment = str(row['mode_of_payment']).strip()
                if mode_of_payment not in ['Cash', 'Credit']:
                    failed_entries.append({
                        'row': int(index) + 2,
                        'error': 'Mode of payment must be Cash or Credit'
                    })
                    continue
                
                # Parse delivery date (optional)
                delivery_date = None
                if 'delivery_date' in row and pd.notna(row['delivery_date']):
                    try:
                        delivery_date = pd.to_datetime(row['delivery_date']).to_pydatetime()
                    except Exception:
                        failed_entries.append({
                            'row': int(index) + 2,
                            'error': 'Invalid delivery date format'
                        })
                        continue
                
                # Create booking
                total_price = product.price * quantity
                
                new_booking = Booking(
                    user_id=customer.id,
                    total_price=total_price,
                    delivery_address_id=address_id,
                    delivery_date=delivery_date,
                    mode_of_payment=mode_of_payment
                )
                db.session.add(new_booking)
                db.session.flush()  # To get the booking ID
                
                # Create booking item
                booking_item = BookingItem(
                    booking_id=new_booking.id,
                    product_id=product.id,
                    quantity=quantity,
                    price_at_purchase=product.price
                )
                db.session.add(booking_item)
                
                # Update product quantity and order count
                product.quantity -= quantity
                product.no_of_orders += quantity
                
                successful_entries += 1
                
            except Exception as e:
                failed_entries.append({
                    'row': int(index) + 2,
                    'error': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Excel upload completed. {successful_entries} entries successful, {len(failed_entries)} failed.',
            'successful_entries': successful_entries,
            'failed_entries': failed_entries
        }), 200 if successful_entries > 0 else 400
        
    except Exception as e:
        return jsonify({'message': f'Error processing Excel file: {str(e)}'}), 500

# Register blueprints in app.py will be done separately
