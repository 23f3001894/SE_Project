# AgriFlow - Agricultural E-commerce Frontend

This is the frontend application for AgriFlow, an agricultural e-commerce platform. This frontend is designed to work **without a backend** - all data is mocked locally for demonstration purposes.

## Features

- **User Authentication**: Login/Register as Customer or Admin
- **Product Catalog**: Browse and search agricultural products
- **Shopping Cart**: Add products to cart and manage quantities
- **Order Management**: Place orders and view order history
- **Address Management**: Save and manage delivery addresses
- **Admin Dashboard**: View statistics, manage products, and analyze sales
- **Demand Forecasting**: Predict future product demand

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
   ```bash
   cd SE_Project-main
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Demo Accounts

The application comes with pre-configured demo accounts:

### Admin Account
- **Email**: admin@agriflow.com
- **Password**: admin123
- **Role**: Admin (Shop Owner)

### Customer Accounts
- **Email**: john@farmer.com
- **Password**: customer123
- **Role**: Customer (Farmer)

- **Email**: jane@retailer.com
- **Password**: customer123
- **Role**: Customer (Retailer)

## Project Structure

```
src/
├── components/        # Reusable UI components
├── context/           # React context (AuthContext)
├── data/             # Mock data
├── pages/            # Page components
│   ├── LoginPage.js
│   ├── AdminDashboard.js
│   ├── CustomerDashboard.js
│   ├── ProductList.js
│   ├── ProductDetails.js
│   ├── CartPage.js
│   ├── OrderHistory.js
│   ├── ProfilePage.js
│   ├── CreateProduct.js
│   ├── EditProduct.js
│   └── ForecastingPage.js
├── services/         # API services
│   ├── api.js        # API configuration
│   └── mockApi.js    # Mock API implementation
└── App.js            # Main application component
```

## Mock Data

The application uses mock data stored in `src/data/mockData.js`. This includes:
- Sample products (fruits, vegetables, grains)
- Demo users (1 admin, 2 customers)
- Cart items and order history
- Addresses

You can modify this file to customize the demo data.

## Available Pages

| Route | Description |
|-------|-------------|
| `/` or `/login` | Login/Registration page |
| `/admin/dashboard` | Admin dashboard with statistics |
| `/customer/dashboard` | Customer dashboard with products |
| `/products` | Product listing page |
| `/products/:id` | Product details page |
| `/products/create` | Create new product (Admin) |
| `/products/:id/edit` | Edit product (Admin) |
| `/cart` | Shopping cart |
| `/orders` | Order history |
| `/profile` | User profile and addresses |
| `/forecasting` | Demand forecasting (Admin) |

## Building for Production

To build the application for production:

```bash
npm run build
```

This will create a `build` folder with the production-ready files.

## Note

This is a frontend-only application. All data is stored locally in memory and will reset when the page is refreshed. For a full production application, you would need to connect to a backend API.
