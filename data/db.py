import sqlite3 as sqlite
from data.models import User, Booking

db = sqlite.connect("data/data.db", check_same_thread=False)


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

def create_user(email: str, username: str, password: str) -> User:
    db.execute("""
               INSERT INTO "users" (email,username,password) VALUES (?,?,?)
               """, (email, username, password))
    db.commit()
    id = db.cursor().lastrowid
    return User(id, email, username, password, "")

def get_user_by_id(id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE id = ?", (id,))
    row = cursor.fetchone()
    return User(*row)

def get_user_by_emailusername(emailusername: str):
    by_email = get_user_by_email(emailusername)
    if by_email != None:
        return by_email
    by_username = get_user_by_username(emailusername)
    return by_username

def get_user_by_email(email: str):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE email = ?", (email,))
    row = cursor.fetchone()
    return User(*row)

def get_user_by_username(username: str):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'users' WHERE username = ?", (username,))
    row = cursor.fetchone()
    return User(*row)