# AgriFlow Backend API

Flask-based REST API backend for the AgriFlow agricultural e-commerce platform.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Navigate to the backend directory:
   ```bash
   cd SE_Project/backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the Flask development server:

```bash
python api.py
```

The server will start at `http://localhost:5000`

The database will be automatically created and seeded with sample data on first run.

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/register` | User registration |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | Get all products |
| GET | `/api/products/<id>` | Get product by ID |
| POST | `/api/products/` | Create product (Admin) |
| PUT | `/api/products/<id>` | Update product (Admin) |
| DELETE | `/api/products/<id>` | Delete product (Admin) |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cart/` | Get user's cart |
| POST | `/api/cart/add` | Add item to cart |
| PUT | `/api/cart/update/<id>` | Update cart item |
| DELETE | `/api/cart/remove/<id>` | Remove from cart |

### Orders/Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bookings/history` | Get order history |
| POST | `/api/bookings/` | Place new order |

### Addresses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/addresses/` | Get user addresses |
| POST | `/api/addresses/` | Create address |
| PUT | `/api/addresses/<id>` | Update address |
| DELETE | `/api/addresses/<id>` | Delete address |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews/product/<id>` | Get product reviews |
| POST | `/api/reviews/` | Create review |

### Admin Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard/stats` | Dashboard statistics |
| GET | `/api/admin/products/expiring` | Expiring products |
| GET | `/api/admin/products/expired` | Expired products |
| GET | `/api/admin/customers/top` | Top customers |
| GET | `/api/admin/customers/credit-scores` | Customer credit scores |
| GET | `/api/admin/recommendations/high-demand` | High demand products |
| GET | `/api/admin/reports/monthly-sales` | Monthly sales report |
| GET | `/api/admin/reports/daily-sales` | Daily sales report |
| GET | `/api/admin/reports/summary` | Sales summary |
| GET | `/api/admin/forecast/demand` | Demand forecast |

## Authentication

The API uses header-based authentication. After login, include these headers in your requests:

- `User-Id`: The user's ID
- `Role`: Either `admin` or `customer`

Example:
```javascript
axios.get('/api/products/', {
  headers: {
    'User-Id': '1',
    'Role': 'admin'
  }
});
```

## Demo Accounts

The database is seeded with these demo accounts:

### Admin Account
- **Email**: admin@agriflow.com
- **Password**: admin123

### Customer Accounts
- **Email**: john@farmer.com
- **Password**: customer123

- **Email**: jane@retailer.com
- **Password**: customer123

## Database

The backend uses SQLite by default, creating a file named `agriflow.db` in the backend directory.

### Database Schema

The database includes the following tables:
- `users` - User accounts
- `addresses` - Delivery addresses
- `products` - Product catalog
- `reviews` - Product reviews
- `bookings` - Orders
- `booking_items` - Order line items
- `cart` - User carts
- `cart_items` - Cart line items

## Connecting Frontend to Backend

1. In the frontend, open `src/services/api.js`

2. Set `USE_MOCK_API` to `false`:
   ```javascript
   const USE_MOCK_API = false;
   ```

3. Start the backend server:
   ```bash
   python api.py
   ```

4. Start the frontend:
   ```bash
   cd ../
   npm start
   ```

## Production Deployment

For production, consider:

1. **Change the secret key** in `api.py`:
   ```python
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-production-secret')
   ```

2. **Use a production database** (PostgreSQL, MySQL):
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/agriflow'
   ```

3. **Add CORS configuration** for production domains

4. **Use a WSGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api:app
   ```
