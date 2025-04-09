import json
import os
import hashlib
import re

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_username(username):
    # Only allow alphanumeric usernames with underscores
    return re.match(r"^[A-Za-z0-9_]+$", username) is not None

def signup(username, password):
    if not is_valid_username(username):
        return False  # Invalid username format
    users = load_users()
    if username in users:
        return False  # Username already exists
    users[username] = {"password": hash_password(password)}
    save_users(users)

    os.makedirs(f"users/{username}/steg", exist_ok=True)
    os.makedirs(f"users/{username}/keys", exist_ok=True)
    os.makedirs(f"users/{username}/extracted", exist_ok=True)
    return True

def login(username, password):
    users = load_users()
    if username not in users:
        return False
    return users[username]["password"] == hash_password(password)
