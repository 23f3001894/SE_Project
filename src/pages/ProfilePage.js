import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const ProfilePage = () => {
  const { user } = useAuth();
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    pin_code: '',
    is_default: false
  });

  useEffect(() => {
    if (user) {
      fetchAddresses();
    }
  }, [user]);

  const fetchAddresses = async () => {
    try {
      const response = await api.get('/addresses/', {
        headers: {
          'User-ID': user.id,
          'Role': user.role
        }
      });
      setAddresses(response.data.addresses);
    } catch (err) {
      console.error('Error fetching addresses:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/addresses/', formData, {
        headers: {
          'User-ID': user.id,
          'Role': user.role
        }
      });
      fetchAddresses();
      setFormData({
        address_line_1: '',
        address_line_2: '',
        city: '',
        state: '',
        pin_code: '',
        is_default: false
      });
      setEditing(false);
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to save address');
    }
  };

  const setDefaultAddress = async (addressId) => {
    try {
      // First, unset all defaults
      await api.put(`/addresses/${addressId}`, {
        is_default: true
      }, {
        headers: {
          'User-ID': user.id,
          'Role': user.role
        }
      });
      fetchAddresses();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to set default address');
    }
  };

  const deleteAddress = async (addressId) => {
    if (!window.confirm('Are you sure you want to delete this address?')) return;
    try {
      await api.delete(`/addresses/${addressId}`, {
        headers: {
          'User-ID': user.id,
          'Role': user.role
        }
      });
      fetchAddresses();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to delete address');
    }
  };

  if (loading) {
    return <div className="profile-page">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <div className="profile-page">
      <h1>My Profile</h1>
      <p>Welcome, {user?.name}!</p>
      <p>Email: {user?.email}</p>
      <p>Phone: {user?.mobile_no || 'Not provided'}</p>
      <p>Total Orders: {user?.no_of_orders || 0}</p>
      
      <div className="section">
        <h2>My Addresses</h2>
        {addresses.length === 0 ? (
          <p>You haven't saved any addresses yet.</p>
        ) : (
          <ul className="addresses-list">
            {addresses.map(address => (
              <li key={address.id} className={`address-item ${address.is_default ? 'default' : ''}`}>
                <div className="address-details">
                  <p><strong>{address.is_default ? '(Default) ' : ''}{address.address_line_1}</strong></p>
                  {address.address_line_2 && <p>{address.address_line_2}</p>}
                  <p>{address.city}, {address.state} {address.pin_code}</p>
                </div>
                <div className="address-actions">
                  {!address.is_default && (
                    <button
                      onClick={() => setDefaultAddress(address.id)}
                      className="btn btn-sm"
                    >
                      Set as Default
                    </button>
                  )}
                  <button
                    onClick={() => deleteAddress(address.id)}
                    className="btn btn-sm btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
        <button onClick={() => setEditing(true)} className="btn btn-primary mt-3">
          Add New Address
        </button>
      </div>
      
      {editing && (
        <div className="address-form">
          <h3>Add New Address</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Address Line 1</label>
              <input
                type="text"
                name="address_line_1"
                value={formData.address_line_1}
                onChange={handleChange}
                required
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>Address Line 2</label>
              <input
                type="text"
                name="address_line_2"
                value={formData.address_line_2}
                onChange={handleChange}
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>City</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                required
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>State</label>
              <input
                type="text"
                name="state"
                value={formData.state}
                onChange={handleChange}
                required
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>PIN Code</label>
              <input
                type="text"
                name="pin_code"
                value={formData.pin_code}
                onChange={handleChange}
                required
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  name="is_default"
                  checked={formData.is_default}
                  onChange={handleChange}
                />
                Set as default address
              </label>
            </div>
            <button type="submit" className="btn btn-primary">
              Save Address
            </button>
            <button
              type="button"
              onClick={() => setEditing(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </form>
        </div>
      )}
      
      <Link to="/" className="btn btn-link mt-4">
        Back to Home
      </Link>
    </div>
    </>
  );
};

export default ProfilePage;