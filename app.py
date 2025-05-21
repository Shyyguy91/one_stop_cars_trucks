from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# --- Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_here' # IMPORTANT: Change this in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable tracking modifications overhead
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Where to redirect if login required

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(255), nullable=True) # Store filename, actual images in static/images
    is_sold = db.Column(db.Boolean, default=False)
    # You can add more fields like transmission, engine, VIN, etc.

    def __repr__(self):
        return f'<Car {self.make} {self.model} ({self.year})>'

# --- Flask-Login User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
@app.route('/home')
def home():
    # Fetch only available cars for the public view
    available_cars = Car.query.filter_by(is_sold=False).order_by(Car.year.desc()).all()
    return render_template('index.html', cars=available_cars)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    all_cars = Car.query.order_by(Car.year.desc()).all()
    return render_template('admin_dashboard.html', cars=all_cars)

@app.route('/add_listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    if request.method == 'POST':
        # A very basic image handling for now - just saving the filename.
        # For a real application, you'd handle file uploads more robustly.
        # Also, make sure to validate all input fields.
        image_file = request.files.get('image_file')
        image_filename = None
        if image_file and image_file.filename != '':
            # In a real app, use a secure filename and save to a specific directory
            # Example: image_filename = secure_filename(image_file.filename)
            # image_file.save(os.path.join(app.root_path, 'static/images', image_filename))
            image_filename = image_file.filename # For simplicity, just use original name
            # !!! WARNING: This is INSECURE for file uploads. Implement proper file handling.

        new_car = Car(
            make=request.form['make'],
            model=request.form['model'],
            year=int(request.form['year']),
            price=float(request.form['price']),
            mileage=int(request.form['mileage']),
            color=request.form.get('color'),
            description=request.form.get('description'),
            image_filename=image_filename
        )
        db.session.add(new_car)
        db.session.commit()
        flash('Car listing added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_listing.html')

@app.route('/edit_listing/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(car_id):
    car = Car.query.get_or_404(car_id)
    if request.method == 'POST':
        car.make = request.form['make']
        car.model = request.form['model']
        car.year = int(request.form['year'])
        car.price = float(request.form['price'])
        car.mileage = int(request.form['mileage'])
        car.color = request.form.get('color')
        car.description = request.form.get('description')
        # Basic image update logic (again, robust handling needed for production)
        image_file = request.files.get('image_file')
        if image_file and image_file.filename != '':
            car.image_filename = image_file.filename # Update filename

        db.session.commit()
        flash('Car listing updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_listing.html', car=car)


@app.route('/delete_listing/<int:car_id>', methods=['POST'])
@login_required
def delete_listing(car_id):
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    flash('Car listing deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/mark_sold/<int:car_id>', methods=['POST'])
@login_required
def mark_sold(car_id):
    car = Car.query.get_or_404(car_id)
    car.is_sold = True
    db.session.commit()
    flash(f'{car.make} {car.model} marked as SOLD!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/mark_available/<int:car_id>', methods=['POST'])
@login_required
def mark_available(car_id):
    car = Car.query.get_or_404(car_id)
    car.is_sold = False
    db.session.commit()
    flash(f'{car.make} {car.model} marked as Available!', 'success')
    return redirect(url_for('admin_dashboard'))

# --- Database Initialization ---
# This block will create the database and a default admin user on first run
with app.app_context():
    db.create_all()
    # Create a default admin user if one doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin')
        admin_user.set_password('adminpassword') # CHANGE THIS PASSWORD IMMEDIATELY!
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user 'admin' created with password 'adminpassword'")
        print("!!! IMPORTANT: CHANGE THIS PASSWORD IMMEDIATELY IN PRODUCTION !!!")


if __name__ == '__main__':
    app.run(debug=True) # debug=True enables auto-reloading and helpful error messages