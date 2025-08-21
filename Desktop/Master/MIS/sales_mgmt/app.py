from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Make CartItem available to all templates
@app.context_processor
def inject_cart_item():
    return dict(CartItem=CartItem)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref='cart_items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    card_last_four = db.Column(db.String(4), nullable=True)
    card_holder_name = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='order_items')
    order = db.relationship('Order', backref='items')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if quantity > product.stock:
        flash('Not enough stock available', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    # Get total items in cart for the message
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    flash(f'Added {quantity} {product.name} to cart. You have {cart_count} item(s) in your cart.', 'success')
    
    # Get the return_to parameter, defaulting to the previous page
    return_to = request.form.get('return_to')
    if return_to:
        return redirect(return_to)
    return redirect(request.referrer or url_for('home'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        return redirect(url_for('cart'))
    
    quantity = int(request.form.get('quantity'))
    if quantity > 0 and quantity <= cart_item.product.stock:
        cart_item.quantity = quantity
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart')
    return redirect(url_for('cart'))

@app.route('/cart/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        # Create order with payment details
        order_data = {
            'user_id': current_user.id,
            'total_amount': total,
            'address': request.form.get('address'),
            'payment_method': payment_method
        }
        
        # Add card details if payment method is card
        if payment_method == 'card':
            card_number = request.form.get('card_number', '').replace(' ', '')
            if len(card_number) != 16:
                flash('Invalid card number', 'error')
                return redirect(url_for('checkout'))
                
            order_data.update({
                'card_last_four': card_number[-4:],
                'card_holder_name': request.form.get('card_name')
            })
            
        order = Order(**order_data)
        db.session.add(order)
        db.session.flush()  # This assigns the ID to the order without committing
        
        try:
            # Create order items and update stock
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                cart_item.product.stock -= cart_item.quantity
                db.session.add(order_item)
                db.session.delete(cart_item)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your order. Please try again.')
            return redirect(url_for('cart'))
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect(url_for('home'))
    return render_template('order_confirmation.html', order=order)

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    users = User.query.all()
    return render_template('admin.html', products=products, orders=orders, users=users)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        new_product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            stock=int(request.form.get('stock')),
            image_url=request.form.get('image_url')
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully')
        return redirect(url_for('admin_panel'))
    return render_template('add_product.html')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.image_url = request.form.get('image_url')
        
        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('admin_panel'))
    
    return render_template('edit_product.html', product=product)

@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully')
    return redirect(url_for('admin_panel'))

def create_initial_data():
    try:
        # Create admin user
        if User.query.filter_by(username='Salma').first() is None:
            admin_user = User(
                username='Salma',
                password=generate_password_hash('master13'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user 'Salma' created successfully!")
        else:
            print("Admin user 'Salma' already exists!")
            
        # Create regular user
        if User.query.filter_by(username='harum').first() is None:
            regular_user = User(
                username='harum',
                password=generate_password_hash('harum123'),
                is_admin=False
            )
            db.session.add(regular_user)
            db.session.commit()
            print("Regular user 'harum' created successfully!")
        else:
            print("Regular user 'harum' already exists!")

        # Check if there are any products
        if Product.query.first() is None:
            products = [
                Product(
                    name='Laptop',
                    description='High-performance laptop with 16GB RAM and 512GB SSD',
                    price=999.99,
                    stock=10,
                    image_url='https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500'
                ),
                Product(
                    name='Smartphone',
                    description='Latest smartphone with 128GB storage',
                    price=699.99,
                    stock=15,
                    image_url='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500'
                ),
                Product(
                    name='Headphones',
                    description='Wireless noise-canceling headphones',
                    price=199.99,
                    stock=20,
                    image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500'
                )
            ]
            db.session.add_all(products)
            db.session.commit()
            print("Sample products created successfully!")
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        create_initial_data()
    app.run(debug=True)
