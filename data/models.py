class User:
    def __init__(self, id, email, username, password, secret_2fa):
        self.id = id
        self.email = email
        self.username = username
        self.password = password
        self.secret_2fa = secret_2fa

class Booking:
    def __init__(self, id, user_id, type, date_time, location, secret):
        self.id = id
        self.user_id = user_id
        self.type = type
        self.date_time = date_time
        self.location = location
        self.secret = secret