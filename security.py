import string, random
import bcrypt

# Firstly, converts the string into bytes
# Then generates a salt and uses it to hash the bytes into a secure string.
def hash(s: str):
    bytes = s.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes, salt)
    return hashed

# Returns True or False dependent on match or not
def check(hashed: str, string: str):
    bytes = string.encode()
    return bcrypt.checkpw(bytes, hashed)

# Generates a random string with (optional) length
def generate_string(l: int = 48):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=l))