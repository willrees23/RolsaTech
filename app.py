from flask import Flask
from data import db

app = Flask(__name__)

db.setup()

@app.route("/")
def landing():
    return "lebron"

if __name__ == "__main__":
    app.run(debug=True)