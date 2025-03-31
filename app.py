from flask import Flask, render_template, request, session, redirect
from flask_session import Session
import time

import security
from data import db
from data.models import Booking, BookingType, User

# create flask instance
# setup the database
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
db.setup()

# setup the application routes

@app.route("/")
def landing():
    user: User = session.get("user")
    if user != None:
        return render_template("landing.html", user=user)
    return render_template("landing.html")

@app.route("/logout")
def logout():
    user: User = session.get("user")
    if user:
        session.clear()
    return redirect("/")

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
            session["user"] = user
            print("Logged in!") 
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # user just submitted the form
        form = request.form
        email = form.get("email")
        username = form.get("username")
        confirm = form.get("confirm_password")
        if not username or not email or not form.get("password") or not confirm:
            error = "All fields are required."
            return render_template("register.html", error=error)
        password = security.hash(form.get("password"))
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
            db.create_user(email, username, password)
        
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)