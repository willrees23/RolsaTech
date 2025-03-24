from flask import Flask
import time

from data import db
from data.models import Booking, BookingType, User

app = Flask(__name__)

db.setup()

@app.route("/")
def landing():
    return "lebron"

if __name__ == "__main__":
    app.run(debug=True)