from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from flask_qrcode import QRcode
from flask_mail import Mail, Message
import time
from datetime import datetime
import pyotp

import security
from data import db
from data.models import Booking, BookingType, User

# store the valid routes for the account tabs
valid_account_routes = ["bookings", "details", "2fa"]
backup_account_route = valid_account_routes[0]

# create flask instance
# setup the database
app = Flask(__name__)

# configure sessions
app.config["SESSION_TYPE"] = "filesystem"

# configure mailing
# Looking to send emails in production? Check out our Email API/SMTP product!
app.config["MAIL_SERVER"] = "sandbox.smtp.mailtrap.io"
app.config["MAIL_PORT"] = 2525
app.config["MAIL_USERNAME"] = "1347987d4a5521"
app.config["MAIL_PASSWORD"] = "6e7c6121e1b2e1"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False


mail = Mail(app)
QRcode(app)
Session(app)
db.setup()

# setup the application routes


@app.route("/")
def landing():
    user: User = session.get("user")
    if user != None:
        return render_template("landing.html", user=user)
    return render_template("landing.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        # make sure that the email is valid
        if email == None or email == "":
            return render_template("reset-password.html", error="An email is required.")

        if "@" not in email or "." not in email:
            return render_template(
                "reset-password.html", error="A valid email is required."
            )

        # tell the user whats going on!
        flash("If it exists in our system, instructions will be sent to: " + email)

        if db.is_email_taken(email):
            # the email is attached to an account, let's send them an email
            user = db.get_user_by_email(email)
            message = Message(
                subject="Password reset request",
                sender="test@test.com",
                recipients=[email],
            )
            message.html = "<h1>test</h1>"
            mail.send(message)

        # we don't really want to tell users that an email has or hasn't been sent, as this gives
        # attackers knowledge as to whether or not that email is being used for an account

        return render_template("reset-password.html")
    else:
        return render_template("reset-password.html")


# The accounts page. Should be accessible via /account or any sub-route such as /account/hello
# If the sub-route isn't valid, it will default to the first valid route ("bookings")
# We pass the route to the page so it knows what to render.
@app.route("/account")
@app.route("/account/<string:option>", methods=["GET", "POST"])
def account(option: str = backup_account_route):
    user: User = session.get("user")
    if request.method == "POST":
        if request.form.get("2fa-code") == "disable":
            db.set_secret(user.email, "")
        else:
            totp = pyotp.TOTP(session.get("new_2fa"))
            if totp.verify(request.form.get("2fa-code")):
                flash("2FA activated.")
                db.set_secret(user.email, session.get("new_2fa"))
            else:
                flash("Invalid 2FA code.")
        session.clear()
        session["user"] = db.get_user_by_email(user.email)
        return redirect("/account/2fa")
    else:
        if user:
            # Check if valid route. If not, default to "bookings".
            if option not in valid_account_routes:
                return redirect("/account/bookings")
            if option == "2fa":
                # user is in the 2FA subroute
                secret_2fa = user.secret_2fa
                if secret_2fa == None or secret_2fa == "":
                    if session.get("new_2fa"):
                        new_2fa = session.get("new_2fa")
                    else:
                        new_2fa = pyotp.random_base32()
                        session["new_2fa"] = new_2fa
                    totp = pyotp.TOTP(new_2fa)
                    uri = totp.provisioning_uri(name=user.email,issuer_name="Rolsa Tech")
                    return render_template(
                        "account.html",
                        user=user,
                        option=option,
                        new_2fa=new_2fa,
                        uri = uri
                    )
                return render_template(
                    "account.html",
                    user=user,
                    option=option,
                    secret_2fa = user.secret_2fa
                )
            elif option == "bookings":
                bookings = db.get_all_bookings_by_user_id(user.id)
                return render_template("account.html", user=user, option=option, bookings=bookings)
            return render_template("account.html", user=user, option=option)
        else:
            return redirect("/login")


@app.route("/logout")
def logout():
    user: User = session.get("user")
    # just clear the session and send them home
    if user:
        session.clear()
    return redirect("/")

@app.route("/login/2fa", methods=["GET", "POST"])
def login2fa():
    if not session.get("2fa_user"):
        return redirect("/login")
    
    user = db.get_user_by_email(session.get("2fa_user"))
    
    if request.method == "POST":
        form = request.form
        code = form.get("2facode")
        totp = pyotp.TOTP(user.secret_2fa)
        if totp.verify(code):
            flash("2FA successful.")
            session.clear()
            session["user"] = user
            return redirect("/")
        else:
            flash("Incorrect 2FA code.")
    return render_template("login2fa.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = request.form
        emailusername = form.get("emailusername")
        password = form.get("password")
        user = db.get_user_by_emailusername(emailusername)
        error = "Email/username or password was incorrect."
        if user == None:
            return render_template("login.html", error=error)
        elif not security.check(user.password, password):
            return render_template("login.html", error=error)
        else:
            # check if they have 2fa active or not.
            # if they do, send them to 2fa checking, if not, log them in
            if user.secret_2fa == None or user.secret_2fa == "":
                session["user"] = user
                flash("You have been logged in. Welcome back, " + user.username)
                return redirect("/")
            else:
                session["2fa_user"] = user.email 
                return redirect("/login/2fa")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        email = form.get("email")
        username = form.get("username")
        confirm = form.get("confirm")

        # let's make sure that everything is first of all present.
        # then we will conduct individual, more specific, validation checks.

        if email == "" or username == "" or confirm == "" or form.get("password") == "":
            error = "All fields are required."
            return render_template("register.html", error=error)
        if "@" not in email or "." not in email:
            error = "A valid email is required."
            return render_template("register.html", error=error)
        password = security.hash(request.form.get("password"))
        if not security.check(password, confirm):
            error = "Passwords do not match."
            return render_template("register.html", error=error)
        elif db.is_email_taken(email):
            error = "Email is already in use."
            return render_template("register.html", error=error)
        elif db.is_username_taken(username):
            error = "Username is already in use."
            return render_template("register.html", error=error)
        else:
            # we've completed the proper checks, we can register the account
            user = db.create_user(email, username, password)
            flash("You have been automatically logged in.")
            session["user"] = user
            return redirect("/")
    else:
        return render_template("register.html")


############
# SERVICES #
############

@app.route("/services/book", methods=["GET", "POST"])
def bookService():
    user: User = session.get("user")
    # check if it's a form submission or not
    if request.method == "POST":
        # get all required data from the form
        form = request.form
        type = form.get("type").upper()
        dt_str = form.get("datetime")
        location = form.get("location")

        # make sure the user has input a location if the booking type is an installation
        if type == "INSTALLATION" and not location:
            flash("Location is required for installations.")
            return redirect("/services/book")

        # we must make sure the date for the booking is in the future.
        try:
            dt = datetime.fromisoformat(dt_str)
            now = datetime.now()

            if dt >= now:
                # it's a valid date, so let's create the booking and tell the user
                db.create_booking(user.id, type, dt.isoformat(), location, security.generate_string())
                flash("Booking created!")
                return redirect("/account/bookings")
            else:
                flash("Invalid date/time.")
        except (ValueError, TypeError):
            flash("Invalid date/time.")
        return redirect("/services/book")

    # not a form submit, so just display the page!
    return render_template("services/book-a-service.html", user = user)



# static page routes
@app.route("/services/consultations")
def consultations():
    user: User = session.get("user")
    return render_template("services/consultations.html", user = user)

@app.route("/services/installations")
def installations():
    user: User = session.get("user")
    return render_template("services/installations.html", user = user)

@app.route("/information/about-green-energy")
def INFO_green_energy():
    user: User = session.get("user")
    return render_template("information/about-green-energy.html", user = user)

@app.route("/information/green-energy-products")
def INFO_green_prodcuts():
    user: User = session.get("user")
    return render_template("information/green-energy-products.html", user = user)

@app.route("/information/reducing-carbon-footprint")
def INFO_carbon_footprint():
    user: User = session.get("user")
    return render_template("information/reducing-carbon-footprint.html", user = user)


if __name__ == "__main__":
    app.run(debug=True)
