import bcrypt
import os, datetime
from dotenv import load_dotenv
import jwt
from functools import wraps
import hashlib
from flask import request, jsonify
from bson import ObjectId
import pytz
import requests
local_timezone = pytz.timezone('Asia/Kolkata')

# Load environment variables from the .env file
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    

def get_indian_time():
    current_utc_time = datetime.datetime.utcnow()
    # Convert the current UTC time to local timezone
    current_local_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    return current_local_time


# Function to securely hash and salt a password
def hash_password(password):
    secret_key = os.getenv("PASSWORD_SECRET_KEY")  # Secret key for Password

    # Generate a random salt and hash the password
    salt = bcrypt.gensalt()
    # Hash the password using the generated salt and bcrypt
    hashed_password_bcrypt = bcrypt.hashpw(password.encode('utf-8'), salt)

    # For added security, hash the hashed_password with the secret key
     # Hash the bcrypt hashed password with the secret key using HMAC
    key_hash = hashlib.pbkdf2_hmac(
        'sha256', hashed_password_bcrypt, secret_key.encode('utf-8'), 100000
    )
    # Convert the derived key to a hex string
    key_hash_hex = key_hash.hex()

    # Convert the bcrypt hashed password to a string
    hashed_password_str = hashed_password_bcrypt.decode('utf-8')

    # Combine the bcrypt hashed password and the derived key as strings
    combined_hash = hashed_password_str + key_hash_hex

    # Return the combined hash
    return combined_hash



# Function to securely verify a password against its hash
def verify_password(password, hashed_password):
    secret_key = os.getenv("PASSWORD_SECRET_KEY")  # Secret key for Password

    # Hash the provided password using the same secret key as the stored hash
    hashed_provided_password = bcrypt.hashpw(password.encode('utf-8'), secret_key.encode('utf-8'))

    # Compare the hashed provided password with the stored hash
    return bcrypt.checkpw(hashed_provided_password, hashed_password)




# Function to check if a user with a given email already exists
def user_exists(db, email):
    # Connect to MongoDB and query the "Users" collection
    collection = db["Users"]
    existing_user = collection.find_one({"email": email})
    return existing_user is not None




# Decorator function to check for authentication (JWT token)
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the JWT token from the Authorization header
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"message": "Unauthorized (no token)"}), 401

        try:
            # Verify the JWT token
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Extract the email from the token's payload
            email = decoded_token.get('email')
            if not email:
                return jsonify({"message": "Invalid token (missing email)"}), 401
            
            # Pass the email to the protected route
            return f(email, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.DecodeError:
            return jsonify({"message": "Invalid token"}), 401
    return decorated


# Example usage: Generate a JWT token with the email as the payload
def generate_jwt_token(email):
    try:
        # Calculate the expiration time (5 minutes from the current local time)
        expiration_time = get_indian_time() + datetime.timedelta(days=1)
        # Convert the expiration time to a Unix timestamp (integer)
        exp_timestamp = int(expiration_time.timestamp())

        # Create the payload
        payload = {
            'email': email,
            'exp': exp_timestamp  # Use the Unix timestamp for expiration time
        }

        # Generate the JWT token
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        # Handle any exceptions
        return str(e)



def convert_to_json(data):
    # Convert ObjectId to its string representation
    if '_id' in data and isinstance(data['_id'], ObjectId):
        data['_id'] = str(data['_id'])

    # Convert other ObjectId values in the document
    def convert_id(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, dict):
            return {k: convert_id(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_id(item) for item in obj]
        return obj

    # Convert all ObjectId values
    converted_data = convert_id(data)

    # Convert to JSON
    json_data = jsonify(converted_data)

    return json_data


# Create a function to fetch data from the external API
def fetch_data_from_api(external_api_url):
    try:
        response = requests.get(external_api_url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        print("Error fetching data from API:", str(e))
        return None


def find_key_ignore_case(data, key):
    for k,v in data.items():
        if k.lower() == key.lower():
            return v
    return None
