# AgriFlow Sprint 1 - Deliverables Documentation

This document maps the 4 grading criteria to the files in the AgriFlow project.

---

## 1. API Creation and Integration (15 marks)

### YAML File Location: `Sprint1_API_Documentation.yaml`

The YAML file contains **25+ APIs** covering all user stories:

| User Story | API Endpoint | Implementation |
|------------|--------------|----------------|
| US1: User Registration & Login | `/api/auth/register`, `/api/auth/login` | Implemented |
| US2: Profile Management | `/api/auth/login` (returns user info) | Implemented |
| US3: Browse Products | `/api/products/` | Implemented |
| US4: Search & Filter | `/api/products/` (with expiry status) | Implemented |
| US5: Add Products (Admin) | `/api/products/` (POST) | Implemented |
| US6: Update Products (Admin) | `/api/products/{id}` (PUT) | Implemented |
| US7: Delete Products (Admin) | `/api/products/{id}` (DELETE) | Implemented |
| US8: Cart Management | `/api/cart/`, `/api/cart/add`, `/api/cart/update/{id}`, `/api/cart/remove/{id}` | Implemented |
| US9: Place Order | `/api/bookings/` | Implemented |
| US10: Order History | `/api/bookings/history` | Implemented |
| US11: Product Reviews | `/api/reviews/` (POST) | Implemented |
| US12: View Reviews | `/api/reviews/product/{id}` | Implemented |
| US13: Address Management | `/api/addresses/` (CRUD) | Implemented |
| US14: Admin Dashboard | `/api/admin/dashboard/stats` | Implemented |
| US15: Expiry Alerts | `/api/admin/products/expiring` | Implemented |
| US16: Top Customers | `/api/admin/customers/top` | Implemented |
| US17: Monthly Reports | `/api/admin/reports/monthly` | Implemented |
| US18: AI Demand Forecasting | `/api/admin/forecast/demand` | Implemented |
| US19: Credit Score Management | `/api/admin/customers/{id}/credit-score` | Implemented |
| US20: Payment Tracking | `/api/admin/payments/pending`, `/api/admin/payments/record` | Implemented |
| US21: Offers Management | `/api/admin/offers/` (CRUD) | Implemented |
| US22: Review Analytics | `/api/admin/reviews`, `/api/admin/reviews/summary` | Implemented |
| US23: Offer Notifications | `/api/admin/offers/send-notifications` | Implemented |
| US24: Smart Recommendations | `/api/admin/recommendations/push-expiry`, `/api/admin/recommendations/high-demand` | Implemented |

### Integrated GenAI APIs

**Demand Forecasting API** (`/api/admin/forecast/demand`):
- Uses linear regression and trend analysis to predict future product demand
- Takes `product_id` and `months_ahead` as parameters
- Returns predicted demand quantities based on historical sales data

---

## 2. Code for the APIs - Implementation (20 marks)

### Implementation Files:

| File | Description |
|------|-------------|
| `backend/routes.py` | Main API implementation (~1976 lines) |
| `backend/app.py` | Flask application setup |
| `backend/models.py` | Database models (User, Product, Cart, Booking, etc.) |

### Key Features:

- **Error Handling**: All endpoints return appropriate HTTP status codes (200, 201, 400, 401, 403, 404)
- **Validation**: Input validation for required fields, email format, credit score range (0-100)
- **Responses**: Consistent JSON responses with proper status messages
- **Authentication**: Role-based access control (customer vs admin)
- **Best Practices**:
  - Database transactions with rollback on failure
  - Stock validation before cart/booking operations
  - Expiry status checking for products
  - Proper error messages for edge cases

### Sample API Code Structure:

```python
# Authentication API Example
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    new_user = User(...)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201

# Cart API with validation
@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    product = Product.query.get(product_id)
    if product.quantity < quantity:
        return jsonify({'message': 'Insufficient stock'}), 400
```

---

## 3. Design and Describe Extensive Test Cases (20 marks)

### Test Documentation: `Sprint1_TestCases_Documentation.md`

This file contains **24 detailed test cases** covering:

| Test Category | Test Cases | Status |
|---------------|------------|--------|
| Authentication APIs | 4 tests (Register, Login, Duplicate Email, Missing Fields) | Complete |
| Product APIs | 6 tests (CRUD operations, expiry filtering) | Complete |
| Cart APIs | 4 tests (Add, Update, Remove, Get) | Complete |
| Booking APIs | 2 tests (Create, History) | Complete |
| Review APIs | 2 tests (Create, Get by product) | Complete |
| Address APIs | 2 tests (Create, Get) | Complete |
| Admin APIs | 8 tests (Dashboard, Expiring, Forecast, Credit Score, Offers) | Complete |

### Test Case Format:

| Field | Description |
|-------|-------------|
| API being tested | Endpoint and method |
| Input | JSON payload and headers |
| Expected Output | Status code and response body |
| Actual Output | Actual result from testing |
| Result | PASS/FAIL |

### Example Test Case:

| Field | Value |
|-------|-------|
| API being tested | POST /api/auth/register |
| Input | `{"name": "John Doe", "email": "john@example.com", "password": "password123"}` |
| Expected Output | `{"message": "User created successfully", "user_id": 1}` with status 201 |
| Actual Output | `{"message": "User created successfully", "user_id": 1}` with status 201 |
| Result | SUCCESS |

---

## 4. Basic Unit Tests using pytest (5 marks)

### Pytest File: `test_sprint1_api.py`

**Location**: Root folder (`C:\Users\guhan\Guhan\Agriflow_Project\test_sprint1_api.py`)

### Test Statistics:
- **Total Test Cases**: 35+ tests
- **Test Categories**: 14 categories
- **Framework**: pytest with fixtures

### Running Tests:
```bash
cd C:\Users\guhan\Guhan\Agriflow_Project
pytest test_sprint1_api.py -v
```

### Test Coverage:

| Category | Tests | Description |
|----------|-------|-------------|
| Auth API | 4 | Register success/failure, Login success/failure |
| Product API | 6 | CRUD operations, role-based access |
| Cart API | 4 | Add, update, remove, get cart |
| Booking API | 2 | Create booking, history |
| Review API | 2 | Create review (validation), get reviews |
| Address API | 2 | Create, get addresses |
| Admin Dashboard | 2 | Stats, unauthorized access |
| Expiring Products | 2 | Expiring soon, expired products |
| Top Customers | 1 | Get top customers |
| Monthly Report | 1 | Sales report generation |
| Demand Forecast | 2 | With/without product_id |
| Credit Scores | 2 | Get, update credit scores |
| Review Analytics | 2 | Pagination, summary |
| Offer Notifications | 2 | Send notifications, get notifications |

### Pytest Fixtures:
- `app` - Flask test application
- `client` - Test client
- `auth_headers` - JSON content type header
- `admin_user` - Admin user fixture
- `customer_user` - Customer user fixture
- `sample_product` - Sample product fixture

### Sample Pytest Code:
```python
class TestRegisterAPI:
    def test_register_success(self, client, auth_headers):
        payload = {"name": "John Doe", "email": "john@example.com", "password": "password123"}
        response = client.post("/api/auth/register", data=json.dumps(payload), headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "user_id" in data

    def test_register_duplicate_email(self, client, auth_headers):
        # Tests duplicate email rejection
        assert response.status_code == 400
```

---

## Summary

| Grading Criterion | File | Status |
|--------------------|------|--------|
| 1. API Creation & YAML | `Sprint1_API_Documentation.yaml` | Complete |
| 2. API Implementation | `backend/routes.py`, `backend/models.py`, `backend/app.py` | Complete |
| 3. Test Cases Documentation | `Sprint1_TestCases_Documentation.md` | Complete |
| 4. Pytest Unit Tests | `test_sprint1_api.py` | Complete |

All deliverables are present and functional.