import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/AdminDashboard';
import CustomerDashboard from './pages/CustomerDashboard';
import ProductList from './pages/ProductList';
import ProductDetails from './pages/ProductDetails';
import CartPage from './pages/CartPage';
import OrderHistory from './pages/OrderHistory';
import ProfilePage from './pages/ProfilePage';
import CreateProduct from './pages/CreateProduct';
import EditProduct from './pages/EditProduct';
import ForecastingPage from './pages/ForecastingPage';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import PublicOnlyRoute from './components/PublicOnlyRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <Routes>
            <Route element={<PublicOnlyRoute />}>
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<LoginPage />} />
            </Route>

            <Route path="/products" element={<ProductList />} />
            <Route path="/products/:id" element={<ProductDetails />} />

            <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
              <Route path="/admin/dashboard" element={<AdminDashboard />} />
              <Route path="/products/create" element={<CreateProduct />} />
              <Route path="/products/:id/edit" element={<EditProduct />} />
              <Route path="/forecasting" element={<ForecastingPage />} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={['customer']} />}>
              <Route path="/customer/dashboard" element={<CustomerDashboard />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={['customer', 'admin']} />}>
              <Route path="/orders" element={<OrderHistory />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
