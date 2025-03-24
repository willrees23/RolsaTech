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
        if user == None:
            print("Invalid credentials")
        elif not security.check(user.password, password):
            print("Invalid credentials")
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
        password = security.hash(form.get("password"))
        confirm = form.get("confirm_password")
        if not security.check(password, confirm):
            print("Passwords do not match")
        elif db.is_email_taken(email):
            print("Email is taken")
        elif db.is_username_taken(username):
            print("Username is taken")
        else:
            # we've completed the proper checks, we can register the account
            db.create_user(email, username, password)
        
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)