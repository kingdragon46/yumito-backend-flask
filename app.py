from flask import Flask, request, jsonify, session, make_response
from pymongo import DESCENDING
import connection
from dotenv import load_dotenv
import os
from flask_session import Session

import qrcode
from tabulate import tabulate
from PIL import Image, ImageDraw

from utils import *

# Load environment variables from the .env file
load_dotenv()


app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'your-secret-key'
Session(app)

app.debug=True

SECRET_KEY = os.getenv("SECRET_KEY")  # Secret key for JWT

# Configure the Flask app to use a session with a specific session type

# Hello World
@app.route('/', methods=['GET'])
def hello_world():
    try:
        return jsonify({"res": "Hello World"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register User
@app.route('/register', methods=['POST'])
def register():
    try:
        print("request: ", request)
        data = request.json
        email = data.get('email')
        password = data.get('password')

        db = connection.connect_to_mongodb()

        # Check if the user with the same email already exists
        if user_exists(db,email):
            return jsonify({"message": "User already exists"}), 400

        hashed_pass = hash_password(password)
        user_data = {
            'email': email,
            "hashedPassword": hashed_pass,
        }
        res = connection.user_register(db, user_data)
        return jsonify({"res": res}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------
# Endpoint to authenticate and get JWT token
@app.route('/login', methods=['POST'])
def login():
    try:
        # Connect to MongoDB
        db = connection.connect_to_mongodb()
        # print("db: ", db)

        # Get email and password from the request
        data = request.json
        email = data.get('email')
        password = data.get('password')

        print(f"Email: {email}")

        check_user = connection.user_login(db, email)

        if not check_user or check_user is False:
            return jsonify({"message": "User does not exist"}), 200
        print("check: ", check_user)

        token = generate_jwt_token(email)

        if session.get("email") is None or session.get("email") == "":
            session["email"]= email

        # In a real application, you should securely hash the password and compare it with the hashed value stored in the database
        # For simplicity, this example does not include password hashing


        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------------------------
# Endpoint to add a food item (requires a valid JWT token)
@app.route('/add_food', methods=['POST'])
# @requires_auth
def add_food(*args,**kwargs):
    try:
        # Connect to MongoDB
        db = connection.connect_to_mongodb()

        # Get food data from the request
        data = request.json
        user_id = session.get('email')

        # if user_id != email:
        #     return  jsonify({"message": "Wrong token with wrong session"}), 404

        # Insert the food item into the MongoDB collection
        data['user_id'] = user_id
        data['created_at'] = get_indian_time()
        connection.insert_data(db, data)

        return jsonify({"message": "Food item added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------------
# Endpoint to retrieve all data from MongoDB
@app.route('/get_all_data', methods=['GET'])
# @requires_auth
def get_all_data(*args,**kwargs):
    try:
        # Connect to MongoDB
        db = connection.connect_to_mongodb()

        # Retrieve all data from the MongoDB collection
        data = connection.get_all_data(db)

        return convert_to_json(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ----------------------------------------------------------------
# Endpoint to retrieve user data from MongoDB
@app.route('/get_user_data', methods=['GET'])
# @requires_auth
def get_data_by_user_id_sorted_by_created_at(*args,**kwargs):
    # Connect to MongoDB
    db = connection.connect_to_mongodb()
    # Assuming you have a "food_items" collection
    collection = db["food_items"]
    user_id = session.get("email")

    # Aggregation pipeline to filter based on user_id and sort by created_at
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$sort": {"created_at": DESCENDING}}
    ]

    # Use the aggregation framework to perform the complex query
    data = list(collection.aggregate(pipeline))
    return convert_to_json(data)
    

# Define routes
@app.route('/clear_session', methods=['GET'])
def clear_session():
    db = connection.connect_to_mongodb()
    # doc ={
    #     # "chat_id":session["chat_id"],
    #     "session":session
    # }
    # data= connection.insert_data(doc,db)

    session.clear()  # Clears all data in the session
    return f'Session cleared'

@app.route('/table_of_contents', methods=['GET'])
def table_of_contents():
    # You can load the HTML file here and return it as a response
    with open('html/qr_response.html', 'r') as html_file:
        html_content = html_file.read()
    
    return html_content, 200, {'Content-Type': 'text/html'}

@app.route('/generate_qr_code', methods=['GET'])
def generate_qr_code():
    # Fetch data from the external API
    # Connect to MongoDB
    db = connection.connect_to_mongodb()

    # Retrieve all data from the MongoDB collection
    data = connection.get_all_data(db)
    print("data: ", data)

    if data is not None:
        # Extracting relevant data and creating a table
        table_data = []
        for item in data:
            table_data.append([
                item["_id"],
                item["name"],
                item["calories"],
                item["description"],
                "\n".join(item["ingredients"]),
                item["price"],
            ])

        # Define table headers
        headers = ["ID", "Name", "Calories", "Description", "Ingredients", "Price"]

        # Generate the table as a string
        table_str = tabulate(table_data, headers, tablefmt="grid")

        # Create a QR code that links to the table_of_contents route
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Construct the URL for the table_of_contents route
        table_of_contents_url = request.url_root + 'table_of_contents'
        
        # Add the URL to the QR code
        qr.add_data(table_of_contents_url)
        qr.make(fit=True)

        # Create an Image object from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the QR code as an image (you can also return it directly in the response)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")

        # Create a Flask response with the image data and set the content type
        response = make_response(img_buffer.getvalue())
        response.headers["Content-Type"] = "image/png"

        return response, 200

    else:
        return jsonify({"error": "Failed to fetch data from the external API"}), 500


if __name__ == '__main__':
    app.run()
