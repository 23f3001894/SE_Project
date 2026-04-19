# SPRINT 1 + SPRINT 2 - COMPLETE TEST CASE DOCUMENTATION (API, FUNCTIONALITY, UNIT)

## 1. Overview

This document is the full, detailed test catalog for:
- `test_api_endpoints.py`
- `test_functionalities.py`
- `test_unit.py`

---

## 2. API Endpoint Tests (`test_api_endpoints.py`)

### 2.1 Authentication API Tests

### Test Case A1: Register Success
Purpose: Verify user registration with valid payload and token issuance.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/register` |
| Input | `{"name":"John Doe","email":"john@example.com","password":"password123","mobile_no":"1234567890"}` |
| Expected Output | Status `201`; response includes `user_id`, `access_token`, message `User created successfully` |
| Actual Output | Assertions validate `201`, token + user id present, expected message present |
| Result | PASS |

### Test Case A2: Register Duplicate Email
Purpose: Ensure duplicate emails are blocked.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/register` |
| Input | Same registration payload submitted twice |
| Expected Output | Status `400`; message includes `Email already exists` |
| Actual Output | Assertion validates `400` and duplicate email message |
| Result | PASS |

### Test Case A3: Register Missing Required Fields
Purpose: Validate request validation for incomplete payload.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/register` |
| Input | `{"name":"John Doe"}` |
| Expected Output | Status `400` |
| Actual Output | Assertion validates `400` |
| Result | PASS |

### Test Case A4: Login Success
Purpose: Validate login with valid credentials for existing user.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/login` |
| Input | `{"email":"customer@agriflow.com","password":"customer123"}` |
| Expected Output | Status `200`; message `Login successful`; includes `user_id`, `access_token`, role `customer` |
| Actual Output | Assertions validate status and response fields |
| Result | PASS |

### Test Case A5: Login Invalid Credentials
Purpose: Ensure wrong credentials are rejected.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/login` |
| Input | `{"email":"wrong@example.com","password":"wrongpass"}` |
| Expected Output | Status `401`; message `Invalid credentials` |
| Actual Output | Assertions validate `401` and expected message |
| Result | PASS |

### Test Case A6: Sprint2 Register Success
Purpose: Sprint 2 smoke validation for registration flow with simplified payload.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/register` |
| Input | `{"name":"Sarwar","email":"sarwar@test.com","password":"1234","role":"customer"}` |
| Expected Output | Status `201` |
| Actual Output | Assertion validates `201` |
| Result | PASS |

### Test Case A7: Sprint2 Register Fail
Purpose: Sprint 2 smoke validation for failed registration due to missing fields.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/register` |
| Input | `{"name":"Sarwar"}` |
| Expected Output | Status `400` |
| Actual Output | Assertion validates `400` |
| Result | PASS |

### Test Case A8: Sprint2 Login Success
Purpose: Sprint 2 smoke validation for login after registration.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/login` |
| Input | Registered user credentials from prior step |
| Expected Output | Status `200` |
| Actual Output | Assertion validates `200` |
| Result | PASS |

### Test Case A9: Sprint2 Login Fail
Purpose: Sprint 2 smoke validation for invalid login.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/auth/login` |
| Input | `{"email":"wrong@test.com","password":"1234"}` |
| Expected Output | Status `401` |
| Actual Output | Assertion validates `401` |
| Result | PASS |

---

### 2.2 Product API Tests

### Test Case P1: Get Products (Customer)
Purpose: Verify public product listing returns product array.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/products/` |
| Input | Customer/public headers |
| Expected Output | Status `200`; `products` key exists and non-empty |
| Actual Output | Assertions validate status + products content |
| Result | PASS |

### Test Case P2: Get Products (Admin)
Purpose: Validate admin listing context and seller attribution.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/products/` |
| Input | Admin auth headers |
| Expected Output | Status `200`; first item `seller_id == admin user id` |
| Actual Output | Assertion validates seller ownership mapping |
| Result | PASS |

### Test Case P3: Get Products Admin Shows Only Owned Products
Purpose: Ensure admin does not see other admin inventory by default.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/products/` |
| Input | Seed one product for current admin + one for another admin |
| Expected Output | Status `200`; own product present, other seller product absent |
| Actual Output | Assertions validate inclusion/exclusion behavior |
| Result | PASS |

### Test Case P4: Get Products Supports Search + Brand Filter
Purpose: Verify filtering/query feature behavior for catalog search.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/products/?search=Harvest&brand=Harvest Hill&sort=popular` |
| Input | Query params for search, brand, sort |
| Expected Output | Status `200`; exactly one matching product with brand `Harvest Hill` |
| Actual Output | Assertions validate filtered response |
| Result | PASS |

### Test Case P5: Create Product Admin Success
Purpose: Ensure admin can create valid product entries.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/products/` |
| Input | Valid product payload with admin auth |
| Expected Output | Status `201`; includes `product_id` |
| Actual Output | Assertions validate status and id field |
| Result | PASS |

### Test Case P6: Create Product Unauthorized
Purpose: Ensure non-admin users cannot create products.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/products/` |
| Input | Customer auth + create payload |
| Expected Output | Status `403` |
| Actual Output | Assertion validates `403` |
| Result | PASS |

### Test Case P7: Get Product Exists
Purpose: Verify single product retrieval by id.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/products/{id}` |
| Input | Existing seeded product id |
| Expected Output | Status `200`; returned product name `Organic Tomatoes` |
| Actual Output | Assertions validate status and name |
| Result | PASS |

### Test Case P8: Get Product Not Found
Purpose: Verify 404 behavior for unknown product id.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/products/99999` |
| Input | Non-existent id |
| Expected Output | Status `404` |
| Actual Output | Assertion validates `404` |
| Result | PASS |

### Test Case P9: Update Product Admin
Purpose: Verify admin can update owned product fields.

| Field | Value |
|-------|-------|
| API being tested | `PUT /api/products/{id}` |
| Input | `{"name":"Updated Tomatoes","price":60.0}` + admin auth |
| Expected Output | Status `200`; message `Product updated` |
| Actual Output | Assertions validate status and message |
| Result | PASS |

### Test Case P10: Delete Product Admin
Purpose: Verify admin can delete owned product.

| Field | Value |
|-------|-------|
| API being tested | `DELETE /api/products/{id}` |
| Input | Existing seeded product id + admin auth |
| Expected Output | Status `200` |
| Actual Output | Assertion validates `200` |
| Result | PASS |

### Test Case P11: Sprint2 Get Products
Purpose: Sprint 2 smoke contract for product list endpoint.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/products/` |
| Input | No auth |
| Expected Output | Status `200` |
| Actual Output | Assertion validates `200` |
| Result | PASS |

### Test Case P12: Sprint2 Create Product Unauthorized
Purpose: Sprint 2 smoke contract for unauthorized create.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/products/` |
| Input | Product payload without admin token |
| Expected Output | Status `401` or `403` |
| Actual Output | Assertion validates status in `[401, 403]` |
| Result | PASS |

---

### 2.3 Cart API Tests

### Test Case C1: Add to Cart Success
Purpose: Verify customer can add available stock to cart.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/cart/add` |
| Input | `{"product_id": seeded_id, "quantity": 2}` + customer auth |
| Expected Output | Status `200` |
| Actual Output | Assertion validates `200` |
| Result | PASS |

### Test Case C2: Add to Cart Insufficient Stock
Purpose: Validate stock guard in cart add.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/cart/add` |
| Input | Limited product quantity=1, request quantity=5 |
| Expected Output | Status `400`; message includes `Insufficient stock` |
| Actual Output | Assertions validate status and message |
| Result | PASS |

### Test Case C3: Get Cart Empty
Purpose: Verify empty cart returns valid structure.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/cart/` |
| Input | Customer with empty cart |
| Expected Output | Status `200`; `cart_items == []` |
| Actual Output | Assertion validates empty array |
| Result | PASS |

### Test Case C4: Update Cart Item
Purpose: Verify cart item quantity update endpoint.

| Field | Value |
|-------|-------|
| API being tested | `PUT /api/cart/update/{cart_item_id}` |
| Input | Existing cart item + new quantity `5` |
| Expected Output | Status `200` |
| Actual Output | Assertion validates `200` |
| Result | PASS |

### Test Case C5: Remove Cart Item
Purpose: Verify customer can remove cart item.

| Field | Value |
|-------|-------|
| API being tested | `DELETE /api/cart/remove/{cart_item_id}` |
| Input | Existing cart item id |
| Expected Output | Status `200` |
| Actual Output | Assertion validates `200` |
| Result | PASS |

### Test Case C6: Sprint2 Add to Cart Fail
Purpose: Sprint 2 smoke validation for unauthenticated/invalid add to cart.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/cart/add` |
| Input | `{"product_id":1,"quantity":2}` without full auth context |
| Expected Output | Status `400` or `401` |
| Actual Output | Assertion validates status in `[400, 401]` |
| Result | PASS |

---

### 2.4 Booking API Tests

### Test Case B1: Create Booking Empty Cart
Purpose: Ensure checkout cannot proceed with empty cart.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/bookings/` |
| Input | `{"delivery_address_id":1,"mode_of_payment":"Cash"}` with empty cart |
| Expected Output | Status `400`; message contains `Cart is empty` |
| Actual Output | Assertions validate status and message |
| Result | PASS |

### Test Case B2: Get Booking History Customer
Purpose: Verify history endpoint returns list structure for customer.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/bookings/history` |
| Input | Customer auth |
| Expected Output | Status `200`; response contains `bookings` |
| Actual Output | Assertions validate status and field |
| Result | PASS |

### Test Case B3: Sprint2 Booking Fail
Purpose: Sprint 2 smoke validation for failed booking without proper prerequisites/auth.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/bookings/` |
| Input | `{"delivery_address_id":1,"mode_of_payment":"COD"}` |
| Expected Output | Status `400` or `401` |
| Actual Output | Assertion validates status in `[400, 401]` |
| Result | PASS |

---

### 2.5 Review API Tests

### Test Case R1: Create Review Without Purchase
Purpose: Enforce purchase-before-review rule.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/reviews/` |
| Input | Customer reviews product not purchased |
| Expected Output | Status `403`; message mentions `purchase` |
| Actual Output | Assertions validate status and message pattern |
| Result | PASS |

### Test Case R2: Get Product Reviews
Purpose: Verify public review listing endpoint works.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/reviews/product/{id}` |
| Input | Existing product id |
| Expected Output | Status `200`; `reviews` key present |
| Actual Output | Assertions validate status and key |
| Result | PASS |

---

### 2.6 Address API Tests

### Test Case AD1: Create Address
Purpose: Verify customer can add delivery address.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/addresses/` |
| Input | Valid address payload with customer auth |
| Expected Output | Status `201` |
| Actual Output | Assertion validates `201` |
| Result | PASS |

### Test Case AD2: Get Addresses
Purpose: Verify customer can fetch own addresses.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/addresses/` |
| Input | Customer auth |
| Expected Output | Status `200`; `addresses` key present |
| Actual Output | Assertions validate status and key |
| Result | PASS |

---

### 2.7 Admin Dashboard / Reports / Forecast / Credit / Delivery Tests

### Test Case AM1: Dashboard Stats
Purpose: Validate admin statistics endpoint contract.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/dashboard/stats` |
| Input | Admin auth |
| Expected Output | Status `200`; includes `total_products`, `total_users`, `total_orders` |
| Actual Output | Assertions validate required keys |
| Result | PASS |

### Test Case AM2: Dashboard Unauthorized
Purpose: Ensure customer cannot access admin dashboard.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/dashboard/stats` |
| Input | Customer auth |
| Expected Output | Status `403` |
| Actual Output | Assertion validates `403` |
| Result | PASS |

### Test Case AM3: Get Expiring Products
Purpose: Validate expiring products admin endpoint.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/products/expiring` |
| Input | Admin auth |
| Expected Output | Status `200`; `expiring_products` key |
| Actual Output | Assertions validate status and key |
| Result | PASS |

### Test Case AM4: Get Expired Products
Purpose: Validate expired products admin endpoint.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/products/expired` |
| Input | Admin auth |
| Expected Output | Status `200`; `expired_products` key |
| Actual Output | Assertions validate status and key |
| Result | PASS |

### Test Case AM5: Get Top Customers
Purpose: Validate top customers analytics endpoint.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/customers/top` |
| Input | Admin auth |
| Expected Output | Status `200`; `top_customers` key |
| Actual Output | Assertions validate status and key |
| Result | PASS |

### Test Case AM6: Get Monthly Report
Purpose: Validate monthly report endpoint structure.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/reports/monthly` |
| Input | Admin auth |
| Expected Output | Status `200`; includes `total_sales`, `total_orders` |
| Actual Output | Assertions validate required keys |
| Result | PASS |

### Test Case AM7: Forecast Demand Success
Purpose: Validate demand forecast generation with product id.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/forecast/demand?product_id={id}&months_ahead=3` |
| Input | Admin auth + valid query params |
| Expected Output | Status `200`; `forecast` key present |
| Actual Output | Assertions validate status and forecast key |
| Result | PASS |

### Test Case AM8: Forecast Missing Product ID
Purpose: Validate bad request handling for missing mandatory param.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/forecast/demand?months_ahead=3` |
| Input | Admin auth, no product_id |
| Expected Output | Status `400` |
| Actual Output | Assertion validates `400` |
| Result | PASS |

### Test Case AM9: Forecast Alias Endpoint by Product ID
Purpose: Validate alternate forecast route and payload identity.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/forecast-demand/{id}?months_ahead=3` |
| Input | Admin auth + product id |
| Expected Output | Status `200`; response `product_id` matches and includes `forecast` |
| Actual Output | Assertions validate id and key |
| Result | PASS |

### Test Case AM10: Get Credit Scores
Purpose: Validate admin customer credit-score listing endpoint.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/customers/credit-scores` |
| Input | Admin auth |
| Expected Output | Status `200`; `customers` key present |
| Actual Output | Assertions validate status and key |
| Result | PASS |

### Test Case AM11: Update Credit Score
Purpose: Validate credit-score update endpoint with valid value.

| Field | Value |
|-------|-------|
| API being tested | `PUT /api/admin/customers/{id}/credit-score` |
| Input | `{"credit_score":75}` + admin auth |
| Expected Output | Status `200` |
| Actual Output | Assertion validates `200` |
| Result | PASS |

### Test Case AM12: Mark Owned Order Delivered
Purpose: Ensure admin can mark own-seller order delivered.

| Field | Value |
|-------|-------|
| API being tested | `PUT /api/admin/orders/{booking_id}/deliver` |
| Input | Booking containing admin-owned product |
| Expected Output | Status `200`; message `Order marked as delivered`; DB status becomes `delivered` |
| Actual Output | Assertions validate response + DB state |
| Result | PASS |

---

### 2.8 Review Analytics & Offer Notification Tests

### Test Case RA1: Get All Reviews with Pagination
Purpose: Validate admin review list endpoint with pagination params.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/reviews?page=1&per_page=10` |
| Input | Admin auth; optionally seeded review |
| Expected Output | Status `200`; `reviews` key present |
| Actual Output | Assertions validate status and key |
| Result | PASS |

### Test Case RA2: Get Reviews Summary
Purpose: Validate review analytics summary contract.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/reviews/summary` |
| Input | Admin auth |
| Expected Output | Status `200`; includes `total_reviews`, `average_rating`, `rating_distribution` |
| Actual Output | Assertions validate required keys |
| Result | PASS |

### Test Case ON1: Send Offer Notifications
Purpose: Verify admin can dispatch offer notifications to customers.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/admin/offers/send-notifications` |
| Input | Active offer id in payload |
| Expected Output | Status `200`; response includes `notifications_sent` |
| Actual Output | Assertions validate status and key |
| Result | PASS |

### Test Case ON2: Get Offer Notifications
Purpose: Verify customer can fetch own offer notifications.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/bookings/notifications/offers` |
| Input | Customer auth |
| Expected Output | Status `200`; `offer_notifications` key present |
| Actual Output | Assertions validate status and key |
| Result | PASS |

---

## 3. Functionality Tests (`test_functionalities.py`)

### Test Case F1: Cart Enforces Single Seller Rule
Purpose: Validate cross-seller mixing in one cart is blocked.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/cart/add` (twice) |
| Input | First add from seller A, second add from seller B |
| Expected Output | First call `200`; second call `400` with one-seller message |
| Actual Output | Assertions validate both status transitions + error message |
| Result | PASS |

### Test Case F2: Booking Updates Inventory and Customer Metrics
Purpose: Validate booking transaction side effects in DB.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/cart/add`, `POST /api/bookings/` |
| Input | Add qty=3, then place booking |
| Expected Output | Booking `201`; DB changes: product qty decremented, product orders incremented, customer order count + spend updated, cart cleared |
| Actual Output | Assertions validate all DB side effects (`97`, `3`, `1`, `150.0`, cart items `0`) |
| Result | PASS |

### Test Case F3: Admin Can Only Deliver Owned Orders
Purpose: Enforce seller ownership boundary in order delivery action.

| Field | Value |
|-------|-------|
| API being tested | `PUT /api/admin/orders/{id}/deliver` |
| Input | One booking for same admin product, another for different admin product |
| Expected Output | Owned booking delivery `200`; non-owned booking delivery `403`; owned booking DB status `delivered` |
| Actual Output | Assertions validate expected status behavior and DB status |
| Result | PASS |

### Test Case F4: Offer Notification Read Flow Ownership
Purpose: Ensure user cannot mark another user's offer notification as read.

| Field | Value |
|-------|-------|
| API being tested | `PUT /api/bookings/notifications/offers/{id}/read` |
| Input | Read own notification id and another user's notification id |
| Expected Output | Own notification `200`; other user's notification `403`; own record marked read with timestamp |
| Actual Output | Assertions validate status checks and DB read fields |
| Result | PASS |

### Test Case AF1: Admin Product Management Workflow
Purpose: Test full admin workflow for product creation, update, customer interaction, and deletion.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/products/`, `PUT /api/products/{id}`, `POST /api/cart/add`, `DELETE /api/products/{id}` |
| Input | Admin creates product, updates it, customer adds to cart, admin deletes product |
| Expected Output | All operations succeed; product deleted from DB |
| Actual Output | Assertions validate each step and final DB state |
| Result | PASS |

### Test Case AF2: Admin Dashboard and Reporting Workflow
Purpose: Validate admin dashboard stats, reports, and top customers after customer purchase.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/bookings/`, `GET /api/admin/dashboard/stats`, `GET /api/admin/reports/monthly`, `GET /api/admin/customers/top` |
| Input | Customer makes purchase, admin checks stats and reports |
| Expected Output | All endpoints return valid data with purchase reflected |
| Actual Output | Assertions validate response structures and data presence |
| Result | PASS |

### Test Case AF3: Admin Forecast and Credit Management Workflow
Purpose: Test admin forecasting and customer credit score management.

| Field | Value |
|-------|-------|
| API being tested | `GET /api/admin/forecast/demand`, `PUT /api/admin/customers/{id}/credit-score`, `GET /api/admin/customers/credit-scores` |
| Input | Admin forecasts demand, updates credit score, retrieves scores |
| Expected Output | Forecast returns valid data; credit update succeeds; scores retrieved |
| Actual Output | Assertions validate forecast length and credit operations |
| Result | PASS |

### Test Case AF4: Admin Offer Notification Workflow
Purpose: Test admin notification sending for existing offers and customer retrieval.

| Field | Value |
|-------|-------|
| API being tested | `POST /api/admin/offers/send-notifications`, `GET /api/bookings/notifications/offers` |
| Input | Admin sends notifications for active offer, customer checks notifications |
| Expected Output | Notifications sent; customer sees notifications |
| Actual Output | Assertions validate sending and retrieval |
| Result | PASS |

---

## 4. Unit Tests (`test_unit.py`)

### 4.1 Auth Service / Model Unit Tests

### Test Case UAuth1: Normalize Role Aliases and Invalid Values
Purpose: Validate role normalization contract used by auth flow.

| Field | Value |
|-------|-------|
| API/Function being tested | `auth_service.normalize_role` |
| Input | Param cases: `admin`, `seller`, `customer`, `buyer`, `invalid` |
| Expected Output | `admin`, `admin`, `customer`, `customer`, `None` respectively |
| Actual Output | Parametrized assertions validate exact mapping for all 5 inputs |
| Result | PASS |

### Test Case UAuth2: Create User Normalizes Email and Creates Cart
Purpose: Ensure helper applies normalization/hashing and creates default cart.

| Field | Value |
|-------|-------|
| API/Function being tested | `auth_service.create_user` |
| Input | Name/email with extra spaces and uppercase; password `secret123`; role `customer` |
| Expected Output | Trimmed name, lowercased email, hashed password, `check_password` true, cart exists |
| Actual Output | Assertions validate each expected property |
| Result | PASS |

### Test Case UAuth3: Legacy Plaintext Password Check
Purpose: Preserve backward compatibility for legacy plaintext password records.

| Field | Value |
|-------|-------|
| API/Function being tested | `User.check_password` |
| Input | User with `password="plainpass"`, check with `plainpass` and `wrong` |
| Expected Output | True for correct plaintext; False for wrong value |
| Actual Output | Assertions validate both outcomes |
| Result | PASS |

### Test Case UAuth4: Create User with Admin Role
Purpose: Validate user creation with admin role and cart assignment.

| Field | Value |
|-------|-------|
| API/Function being tested | `auth_service.create_user` |
| Input | Name, email, password, role="admin" |
| Expected Output | User with admin role, cart created |
| Actual Output | Assertions validate role and cart presence |
| Result | PASS |

### Test Case UAuth5: Create User Handles Duplicate Email
Purpose: Ensure duplicate emails raise exceptions.

| Field | Value |
|-------|-------|
| API/Function being tested | `auth_service.create_user` |
| Input | Two users with same email |
| Expected Output | Exception raised for duplicate |
| Actual Output | Pytest raises exception assertion |
| Result | PASS |

### Test Case UAuth6: User Check Password with Hashed Password
Purpose: Validate password checking with properly hashed passwords.

| Field | Value |
|-------|-------|
| API/Function being tested | `User.check_password` |
| Input | User with hashed password, check correct and wrong passwords |
| Expected Output | True for correct; False for wrong |
| Actual Output | Assertions validate password verification |
| Result | PASS |

---

### 4.2 Forecast Service Unit Tests

### Test Case UF1: Demand Forecast Uses Moving Average with History
Purpose: Validate standard forecasting method when enough historical points exist.

| Field | Value |
|-------|-------|
| API/Function being tested | `forecast_service.build_demand_forecast` |
| Input | Product + 3 monthly bookings with quantities `12,18,30`; `months_ahead=3` |
| Expected Output | Method `moving_average`; `historical_data_points=3`; forecast length `3`; each quantity >= 1 |
| Actual Output | Assertions validate method, history count, forecast length, and bounds |
| Result | PASS |

### Test Case UF2: Demand Forecast Uses Fallback Without History
Purpose: Validate fallback forecasting mode for sparse/no history.

| Field | Value |
|-------|-------|
| API/Function being tested | `forecast_service.build_demand_forecast` |
| Input | Product + empty bookings; `months_ahead=2` |
| Expected Output | Method `moving_average_fallback`; history `0`; forecast length `2`; confidence `low` |
| Actual Output | Assertions validate fallback mode and output structure |
| Result | PASS |

### Test Case UF3: Demand Forecast with Insufficient History
Purpose: Validate fallback for less than 3 historical data points.

| Field | Value |
|-------|-------|
| API/Function being tested | `forecast_service.build_demand_forecast` |
| Input | Product + 2 bookings; `months_ahead=3` |
| Expected Output | Method `moving_average_fallback`; history `2`; forecast length `3` |
| Actual Output | Assertions validate fallback mode |
| Result | PASS |

### Test Case UF4: Demand Forecast with Zero Quantity Product
Purpose: Ensure forecast works for products with zero stock.

| Field | Value |
|-------|-------|
| API/Function being tested | `forecast_service.build_demand_forecast` |
| Input | Product with quantity=0; empty bookings; `months_ahead=1` |
| Expected Output | Method `moving_average_fallback`; history `0`; forecast length `1`; predicted_quantity >=1 |
| Actual Output | Assertions validate output |
| Result | PASS |

### Test Case UF5: Demand Forecast Multiple Products in Bookings
Purpose: Validate forecast filters correctly for specific product.

| Field | Value |
|-------|-------|
| API/Function being tested | `forecast_service.build_demand_forecast` |
| Input | Product + bookings with multiple products; `months_ahead=2` |
| Expected Output | History points =2; method `moving_average_fallback` |
| Actual Output | Assertions validate filtering |
| Result | PASS |

---

### 4.3 Reporting Service Unit Tests

### Test Case UR1: Top Customers Ranking by Orders Then Spend
Purpose: Validate leaderboard ranking logic used in admin analytics.

| Field | Value |
|-------|-------|
| API/Function being tested | `reporting_service.build_admin_top_customers` |
| Input | Seed admin, two customers, product, addresses, 3 bookings with booking items |
| Expected Output | Top list length `2`; customer A ranked first with `2` orders; customer B second |
| Actual Output | Assertions validate ordering and order counts |
| Result | PASS |

### Test Case UR2: Sales Summary with Zero Orders
Purpose: Ensure summary endpoint helper is safe when there are no bookings.

| Field | Value |
|-------|-------|
| API/Function being tested | `reporting_service.build_sales_summary` |
| Input | Admin with no orders |
| Expected Output | `total_orders_this_month == 0`, `avg_order_value == 0` |
| Actual Output | Assertions validate zero-safe summary behavior |
| Result | PASS |

### Test Case UR3: Sales Summary with Orders
Purpose: Validate summary calculations with actual orders.

| Field | Value |
|-------|-------|
| API/Function being tested | `reporting_service.build_sales_summary` |
| Input | Admin with customer order |
| Expected Output | Correct total_orders, revenue, avg_order_value |
| Actual Output | Assertions validate calculations |
| Result | PASS |

### Test Case UR4: Monthly Sales with Multiple Months
Purpose: Test monthly sales aggregation across different months.

| Field | Value |
|-------|-------|
| API/Function being tested | `reporting_service.build_monthly_sales` |
| Input | Admin with bookings in different months |
| Expected Output | Series with 2 months, correct revenue and orders |
| Actual Output | Assertions validate multi-month data |
| Result | PASS |

---

## 5. Coverage Summary

| Test File | Total Tests Documented |
|-----------|------------------------|
| `test_api_endpoints.py` | 51 |
| `test_functionalities.py` | 8 |
| `test_unit.py` | 14 |
| **Grand Total** | **73** |

