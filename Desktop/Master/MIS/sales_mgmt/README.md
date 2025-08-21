# E-Commerce Website

A dynamic e-commerce website built with Flask that allows customers to view products, place orders, and managers to control the website.

## Features

- User authentication (login/register)
- Product listing and details
- Shopping cart functionality
- Admin panel for product and order management
- Stock management
- Responsive design using Bootstrap

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```
     source .venv/bin/activate
     ```
4. Install required packages:
   ```
   pip install flask flask-sqlalchemy flask-login werkzeug
   ```

## Running the Application

1. Run the Flask application:
   ```
   python app.py
   ```
2. Open your web browser and navigate to `http://127.0.0.1:5000`

## Default Admin User

To create an admin user, you'll need to:
1. Register a new user through the website
2. Access the SQLite database and set the `is_admin` field to `True` for your user

## Database

The application uses SQLite as its database. The database file (`ecommerce.db`) will be created automatically when you first run the application.
