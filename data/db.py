import sqlite3 as sqlite
from data.models import User, Booking

# Connects to the database.
# check_same_thread stops an error from occurring.
db = sqlite.connect("data/data.db", check_same_thread=False)


# Ran on application start.
# Sets up the database by creating the necessary tables (if they don't already exist)
def setup():
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS "users" (
        "id"	INTEGER,
        "email"	TEXT UNIQUE,
        "username"	TEXT UNIQUE,
        "password"	TEXT,
        "2fa_secret"	TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS "bookings" (
        "id"	INTEGER,
        "user_id"	TEXT,
        "type"	TEXT,
        "date_time"	TEXT,
        "location"	TEXT,
        "secret"	TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
    )

# Inserts a new user into the database and returns a User object
def create_user(email: str, username: str, password: str) -> User:
    db.execute("""
               INSERT INTO "users" (email,username,password) VALUES (?,?,?)
               """, (email, username, password))
    db.commit()
    # Get the last row that was inserted and get it's ID.
    id = db.cursor().lastrowid
    return User(id, email, username, password, "")

def is_email_taken(email: str) -> bool:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE email = ?", (email,))
    return cursor.fetchone() != None

def is_username_taken(username: str) -> bool:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE username = ?", (username,))
    return cursor.fetchone() != None

# Retreives a user from the database using the ID
def get_user_by_id(id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE id = ?", (id,))
    row = cursor.fetchone()
    return User(*row)

# Retreives a user f rom the database using either the username or email.
# First tries to get via email, if it fails, it will try using the username.
def get_user_by_emailusername(emailusername: str):
    try:
        by_email = get_user_by_email(emailusername)
        if by_email != None:
            return by_email
    except:
        pass
    
    try:
        by_username = get_user_by_username(emailusername)
    except:
        pass
    return by_username

# Retreives a user from the database using the email.
def get_user_by_email(email: str):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE email = ?", (email,))
    row = cursor.fetchone()
    return User(*row)

# Retreives a user from the database using the email.
def get_user_by_username(username: str):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE username = ?", (username,))
    row = cursor.fetchone()
    return User(*row)


### Booking related functions ###

# Inserts a new booking entry into the database
def create_booking(user_id, type, date_time, location, secret) -> Booking:
    db.execute("""
               INSERT INTO "bookings" (user_id,type,date_time,location,secret) VALUES (?,?,?,?,?)
               """, (user_id, type, date_time, location, secret))
    db.commit()
    # Get the last row that was inserted and get it's ID.
    id = db.cursor().lastrowid
    return Booking(id, user_id, type, date_time, location, secret)

# Retreives a booking from the database using the ID.
def get_booking_by_id(id) -> Booking:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'bookings' WHERE id = ?", (id,))
    row = cursor.fetchone()
    return Booking(*row)

# Retreives a booking from the database using the user ID
def get_booking_by_user_id(user_id) -> Booking:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'bookings' WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return Booking(*row)

# Retreives all the bookings from the database using the user ID
def get_all_bookings_by_user_id(user_id) -> list[Booking]:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'bookings' WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    bookings = []
    for row in rows:
        bookings.append(Booking(*row))
    return bookings