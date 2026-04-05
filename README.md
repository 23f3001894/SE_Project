# AgriFlow - Agricultural E-commerce Platform

AgriFlow is a full-stack agricultural e-commerce platform connecting farmers with customers. It includes a Flask backend API and React frontend.

## Features

- **User Authentication**: Register/Login as Customer or Admin
- **Product Management**: Browse, create, update, and delete products (Admin)
- **Shopping Cart**: Add products, update quantities, remove items
- **Order Management**: Place orders, view order history
- **Address Management**: Save and manage delivery addresses
- **Product Reviews**: Rate and review purchased products
- **Admin Dashboard**: Statistics, product management, sales analytics
- **AI Demand Forecasting**: Predict future product demand using linear regression
- **Credit Score Management**: Track and update customer credit scores
- **Offer Management**: Create and manage promotional offers
- **Offer Notifications**: Push notifications to customers
- **Review Analytics**: Rating distribution, top-rated products

## Tech Stack

- **Backend**: Flask (Python) with SQLite database
- **Frontend**: React.js
- **Testing**: pytest (35+ unit tests)

## Project Structure

```
Agriflow/
├── backend/                 # Flask API
│   ├── app.py              # Application setup
│   ├── models.py          # Database models
│   ├── routes.py          # API endpoints
│   ├── requirements.txt   # Python dependencies
│   └── instance/          # SQLite database
├── frontend/               # React application
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── context/      # Auth context
│   │   ├── pages/        # Page components
│   │   └── services/     # API services
│   └── package.json
├── test_sprint1_api.py     # Pytest unit tests
├── Sprint1_API_Documentation.yaml  # API documentation
├── Sprint1_TestCases_Documentation.md
└── Sprint1_Deliverables_Explanation.md
```

## Getting Started

### Backend Setup

1. Navigate to backend folder:
   ```bash
   cd backend
   ```

2. Create virtual environment (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   python app.py
   ```

5. Backend runs at: http://localhost:5000

### Frontend Setup

1. Navigate to frontend folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Frontend runs at: http://localhost:3000

## Demo Accounts

### Admin Account
- **Email**: admin@agriflow.com
- **Password**: admin123
- **Role**: Admin (Shop Owner)

### Customer Account
- **Email**: customer@agriflow.com
- **Password**: customer123
- **Role**: Customer (Farmer/Retailer)

## API Endpoints

| Category | Endpoints |
|----------|-----------|
| Auth | `/api/auth/register`, `/api/auth/login` |
| Products | `/api/products/` (CRUD) |
| Cart | `/api/cart/`, `/api/cart/add`, `/api/cart/update/{id}`, `/api/cart/remove/{id}` |
| Bookings | `/api/bookings/`, `/api/bookings/history` |
| Reviews | `/api/reviews/`, `/api/reviews/product/{id}` |
| Addresses | `/api/addresses/` (CRUD) |
| Admin | Dashboard, forecasting, credit scores, offers, reviews |

## Running Tests

```bash
# Run pytest unit tests
pytest test_sprint1_api.py -v
```

## API Documentation

Full API documentation is available in `Sprint1_API_Documentation.yaml` (OpenAPI format).

## Deliverables

| File | Description |
|------|-------------|
| `Sprint1_API_Documentation.yaml` | OpenAPI specification for all endpoints |
| `Sprint1_TestCases_Documentation.md` | Detailed test cases with input/output |
| `Sprint1_Deliverables_Explanation.md` | Grading criteria mapping |
| `test_sprint1_api.py` | Pytest unit test suite (35+ tests) |

## Building for Production

### Frontend
```bash
cd frontend
npm run build
```

### Backend
The backend can be deployed using any WSGI server (gunicorn, uwsgi, etc.):
```bash
cd backend
gunicorn -w 4 app:app
```