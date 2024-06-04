from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, logout_user, login_required


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site1.db'
app.config['SECRET_KEY'] = 'welcometothehell'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    shopping_cart = db.relationship('ShoppingCart', backref='user', lazy=True, cascade='all, delete-orphan')
    order = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return '<User %r>' % self.id

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    reviews = db.relationship('Review', backref='book', lazy=True, cascade='all, delete-orphan')
    def __repr__(self):
        return '<Book %r>' % self.id

    def add_to_cart(self, user_id, quantity=1):
        cart_item = ShoppingCart.query.filter_by(user_id=user_id, book_id=self.id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = ShoppingCart(user_id=user_id, book_id=self.id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    def __repr__(self):
        return '<Review %r>' % self.id

class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    book = db.relationship('Book', backref='cart_items')

    def __repr__(self):
        return '<ShoppingCart %r>' % self.id

    @classmethod
    def remove_from_cart(cls, item_id):
        cart_item = cls.query.get_or_404(item_id)
        db.session.delete(cart_item)
        db.session.commit()

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Очікується')
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    total_price = db.Column(db.Float, nullable=False)
    def __repr__(self):
        return '<Order %r>' % self.id

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    book = db.relationship('Book')
    def __repr__(self):
        return '<OrderItem %r>' % self.id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('homepage'))
        else:
            flash('Неправильний логін або пароль', 'Помилка')
    return render_template('login.html')

@app.route('/guest_login', methods=['POST'])
def guest_login():
    return redirect(url_for('homepage'))
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        uniq_user = User.query.filter_by(username=username).first()
        if uniq_user:
            flash('Користувач з таким логіном вже існує', 'Помилка')
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            flash('Виникла помилка', 'Помилка')

    else:
        return render_template('register.html')

@app.route('/homepage')
def homepage():
    search_title = request.args.get('searchTitle')
    search_author = request.args.get('searchAuthor')
    genre_filter = request.args.get('genreFilter')
    min_price = request.args.get('minPrice')
    max_price = request.args.get('maxPrice')
    query = Book.query
    if search_title:
        query = query.filter(Book.title.ilike(f'%{search_title}%'))
    if search_author:
        query = query.filter(Book.author.ilike(f'%{search_author}%'))
    if genre_filter and genre_filter != 'All':
        query = query.filter(Book.genre == genre_filter)
    if min_price:
        query = query.filter(Book.price >= float(min_price))
    if max_price:
        query = query.filter(Book.price <= float(max_price))
    books = query.all()
    return render_template('homepage.html', books=books)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

@app.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    rating = int(request.form['rating'])
    content = request.form['content']
    book = Book.query.get_or_404(book_id)

    review = Review(author=current_user.username, rating=rating, content=content, book_id=book.id)
    db.session.add(review)
    db.session.commit()
    return redirect(url_for('book_details', book_id=book.id))

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    book.add_to_cart(user_id=current_user.id)
    return redirect(url_for('book_details', book_id=book.id))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    ShoppingCart.remove_from_cart(item_id)
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        email = request.form['email']
        address = request.form['address']
        phone_number = request.form['phone_number']
        payment_method = request.form['payment_method']
        cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            return redirect(url_for('cart'))
        total_price = sum(item.book.price * item.quantity for item in cart_items)
        order = Order(
            user_id=current_user.id,
            user_name=current_user.username,
            email=email,
            address=address,
            phone_number=phone_number,
            payment_method=payment_method,
            total_price = total_price
        )
        db.session.add(order)
        db.session.commit()
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=item.book_id,
                quantity=item.quantity
            )
            db.session.add(order_item)
            db.session.delete(item)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template('checkout.html')
@app.route('/cart')
@login_required
def cart():
    cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.book.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items,  total_price=total_price)

@app.route('/list_orders')
@login_required
def list_orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('list_orders.html', orders=user_orders)

class NoCreateModelView(ModelView):
    can_create = False

admin = Admin(app, name='bookstore', template_mode='bootstrap3')
admin.add_view(ModelView(Book, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(NoCreateModelView(Order, db.session))
admin.add_view(NoCreateModelView(Review, db.session))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
