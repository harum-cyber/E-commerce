# E-Commerce Website Documentation

## Project Overview
A dynamic e-commerce website built using Python and Flask framework, implementing a complete shopping experience with user authentication, product management, shopping cart functionality, and order processing. The system supports both customer and administrative operations with a responsive, user-friendly interface.

## Technical Architecture

### Backend Technologies
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login
- **Password Security**: Werkzeug security utilities for password hashing

### Frontend Technologies
- **UI Framework**: Bootstrap 5.1.3
- **Icons**: Font Awesome 6.0.0
- **JavaScript**: Vanilla JS for dynamic interactions
- **Templates**: Jinja2 templating engine

### Database Schema
1. **User Model**
   - Fields: id, username, password (hashed), is_admin
   - Supports both regular users and administrators

2. **Product Model**
   - Fields: id, name, description, price, stock, image_url
   - Manages product inventory and details

3. **CartItem Model**
   - Fields: id, user_id, product_id, quantity
   - Handles shopping cart functionality

4. **Order Model**
   - Fields: id, user_id, total_amount, address, payment_method, status, created_at
   - Additional fields for card payments: card_last_four, card_holder_name

5. **OrderItem Model**
   - Fields: id, order_id, product_id, quantity, price
   - Manages individual items within orders

## Core Features

### User Management
1. **Authentication System**
   - User registration with unique username
   - Secure password hashing
   - Session management
   - Role-based access control (Admin/Customer)

2. **Administrative Functions**
   - Product management (CRUD operations)
   - Order monitoring
   - Stock management
   - User order history access

3. **Customer Features**
   - Product browsing
   - Cart management
   - Order placement
   - Order history viewing

### Shopping Experience
1. **Product Display**
   - Grid layout with product images
   - Detailed product views
   - Stock availability
   - Price information

2. **Shopping Cart**
   - Real-time quantity updates
   - Item removal
   - Price calculations
   - Persistent cart storage

3. **Checkout Process**
   - Address collection
   - Payment method selection
   - Card payment processing
   - Order confirmation

### Payment Processing
1. **Payment Options**
   - Cash on Delivery
   - Credit/Debit Card
     - Card number validation
     - Expiry date formatting
     - CVV verification
     - Secure storage (last 4 digits only)

## Security Measures
- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection
- Input validation
- Secure card data handling
- Role-based access control

## User Interface
- Responsive design using Bootstrap
- Pink-themed color scheme
- Interactive feedback messages
- Mobile-friendly layout
- Intuitive navigation
- Clear error messaging

## File Structure
```
sales_mgmt/
├── app.py              # Main application file
├── instance/          
│   └── ecommerce.db   # SQLite database
├── static/            # Static assets
├── templates/         # HTML templates
│   ├── admin.html
│   ├── base.html
│   ├── cart.html
│   ├── checkout.html
│   ├── home.html
│   ├── login.html
│   ├── product_detail.html
│   ├── register.html
│   └── order_confirmation.html
└── README.md
```

## Development Workflow
1. Database initialization with sample data
2. User authentication setup
3. Product management implementation
4. Shopping cart functionality
5. Order processing system
6. Admin panel creation
7. Payment processing integration

## Best Practices Implemented
- Modular code structure
- Database relationship modeling
- Secure password handling
- Clean code principles
- Responsive design patterns
- Error handling
- User feedback
- Form validation

## Future Enhancements
- Payment gateway integration
- Email notifications
- Product categories
- Search functionality
- User profiles
- Order tracking
- Reviews and ratings
- Wishlist feature
