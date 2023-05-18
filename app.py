from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta

app = Flask(__name__)
login_manager = LoginManager(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel.db"
app.secret_key = (
    "\xec\xe7\xb5V\x13\x14u\x10-\x9a\xe1\x14\xd8\x02P\x93\x81\x14\x912\xd5\x86DS"
)
# Set a secret key for session security

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
admin = Admin(app, name="Admin Panel", template_mode="bootstrap3")


class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    bookings = db.relationship("Booking", backref="customer", lazy=True)
    service_requests = db.relationship("ServiceRequest", backref="customer", lazy=True)
    dining_requests = db.relationship("DiningRequest", backref="customer", lazy=True)
    password = db.Column(db.String(150), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    check_in_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_date = db.Column(db.DateTime, nullable=False)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(25), nullable=False, default="Pending")


class DiningRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    check_in_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    bookings = db.relationship("Booking", backref="room", lazy=True)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)


class CustomerModelView(ModelView):
    column_exclude_list = (
        "password",
    )  # Exclude the password field from the admin panel
    column_searchable_list = ("name", "email", "phone")
    column_filters = ("name", "email", "phone")


admin.add_view(CustomerModelView(Customer, db.session))
admin.add_view(ModelView(Booking, db.session))
admin.add_view(ModelView(ServiceRequest, db.session))
admin.add_view(ModelView(DiningRequest, db.session))
admin.add_view(ModelView(Room, db.session))


@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(user_id)


@app.route("/account")
@login_required
def account():
    customer = Customer.query.get(current_user.id)
    bookings = customer.bookings
    service_requests = customer.service_requests
    dining_requests = customer.dining_requests
    return render_template(
        "account.html",
        customer=customer,
        bookings=bookings,
        service_requests=service_requests,
        dining_requests=dining_requests,
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        # Hash the password before storing in the database
        hashed_password = generate_password_hash(password)

        # Create a new user object
        new_user = Customer(
            name=name, email=email, phone=phone, password=hashed_password
        )

        # Add the new user to the database
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Email or phone number already exists"

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("login_username") or request.form.get("username")
        password = request.form.get("login_password") or request.form.get("password")

        # Check if the username (email or phone) exists in the database
        user = Customer.query.filter(
            or_(Customer.email == username, Customer.phone == username)
        ).first()
        print(username)
        print(password)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("account"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/services/spa")
def services_spa():
    return render_template("services_spa.html")


@app.route("/services/fitness-center")
def services_fitness_center():
    return render_template("services_fitness_center.html")


@app.route("/services/fine-dining")
def services_fine_dining():
    return render_template("services_fine_dining.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# Route to handle the form submission
@app.route("/submit-contact", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")

    return render_template("contact_confirmation.html", name=name, email=email)


@app.route("/api/reservations", methods=["POST"])
def make_reservation():
    reservation_data = request.get_json()
    reservation_data["datetime"] = datetime.strptime(
        reservation_data["datetime"], "%Y-%m-%dT%H:%M"
    )
    print(reservation_data)
    # find customer by email
    customer = Customer.query.filter_by(email=reservation_data["email"]).first()
    if not customer:
        # Perform validation and save reservation data to the database
        customer = Customer(
            name=reservation_data["name"],
            email=reservation_data["email"],
            phone=reservation_data["phone"],
        )
        db.session.add(customer)
        db.session.commit()
    # check if customer has existing reservation
    existing_reservation = DiningRequest.query.filter_by(
        customer_id=customer.id
    ).first()
    if existing_reservation:
        return jsonify({"message": "You already have an existing reservation"})

    dining_request = DiningRequest(
        customer_id=customer.id,
        number_of_guests=reservation_data["guests"],
        check_in_date=reservation_data["datetime"],
    )
    db.session.add(dining_request)
    db.session.commit()

    print(customer.id)
    print(dining_request.id)
    print("Reservation successfully made")

    # Return a JSON response indicating the success of the reservation
    return jsonify({"message": "Reservation successfully made"})


@app.route("/rooms")
def rooms():
    rooms = Room.query.all()
    for room in rooms:
        room.description = room.description[:80] + "..."
    return render_template("rooms.html", rooms=rooms)


# Room details and booking page
@app.route("/room", methods=["GET"])
def room():
    room = Room.query.filter_by(id=request.args.get("id")).first()
    if room:
        return render_template(
            "room.html",
            room_id=room.id,
            room_name=room.name,
            room_description=room.description,
            room_image_path=room.image,
            price=room.price,
        )
    else:
        return "Room not found"


class BookingSchema(ma.Schema):
    class Meta:
        fields = ("id", "customer_id", "room_number", "check_in_date", "check_out_date")


@app.route("/get_available_dates", methods=["GET"])
def get_available_dates():
    room_id = request.args.get("id")
    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return jsonify({"error": "Room not found."})

    # Get all the bookings for the room
    bookings = Booking.query.filter_by(room_id=room_id).all()

    # Calculate available dates (you can customize the range as needed)
    available_dates = []
    today = datetime.now().date()
    for i in range(30):
        date = today + timedelta(days=i)
        if not any(
            booking.check_in_date.date() <= date <= booking.check_out_date.date()
            for booking in bookings
        ):
            available_dates.append(date.strftime("%Y-%m-%d"))

    return jsonify({"available_dates": available_dates, "price": room.price})

@app.route("/get_booked_dates", methods=["GET"])
def get_booked_dates():
    room_id = request.args.get("id")
    if not room_id:
        return jsonify({"error": "Invalid room ID."})

    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return jsonify({"error": "Room not found."})

    booked_dates = Booking.query.filter_by(room_id=room_id).all()
    booked_dates_list = [
        {
            "check_in_date": booking.check_in_date.strftime("%Y-%m-%d"),
            "check_out_date": booking.check_out_date.strftime("%Y-%m-%d"),
        }
        for booking in booked_dates
    ]

    return jsonify({"booked_dates": booked_dates_list})

@app.route('/place_order', methods=['POST'])
def place_order():
    room_id = request.form.get('room_id')
    check_in_date = request.form.get('check_in_date')
    check_out_date = request.form.get('check_out_date')

    # Validate the submitted data
    if not room_id or not check_in_date or not check_out_date:
        return jsonify({"error": "Invalid data."})

    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return jsonify({"error": "Room not found."})

    # Check for existing bookings that overlap with the requested dates
    requested_check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
    requested_check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
    existing_bookings = Booking.query.filter_by(room_id=room_id).all()

    for booking in existing_bookings:
        if (booking.check_in_date <= requested_check_in_date < booking.check_out_date) or (
            booking.check_in_date < requested_check_out_date <= booking.check_out_date) or (
            requested_check_in_date <= booking.check_in_date and requested_check_out_date >= booking.check_out_date):
            return jsonify({"error": "The room is already booked for the requested dates."})

    # Create a new booking record
    customer_id = 1  # Replace with the actual customer ID
    booking = Booking(customer_id=customer_id, room_id=room_id, room_number=room.room_number, check_in_date=requested_check_in_date, check_out_date=requested_check_out_date)
    db.session.add(booking)
    db.session.commit()

    return jsonify({"success": True})

@app.route('/book', methods=['GET'])
def book():
    room_id = request.args.get('id')
    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return f"Room with ID {room_id} not found."

    # Render the book.html template with the room ID
    return render_template('book.html', room_id=room_id,
            room_name=room.name,
            room_description=room.description,
            room_image_path=room.image,
            price=room.price,)




if __name__ == "__main__":
    app.run(debug=True)