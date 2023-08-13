import pymongo
from dotenv import load_dotenv
import os


# Load environment variables from the .env file
load_dotenv()

# Get the MongoDB connection string from the environment variables
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")


# Connect to the MongoDB database using a connection string
def connect_to_mongodb(connection_string=MONGODB_CONNECTION_STRING):
    client = pymongo.MongoClient(connection_string)
    db = client.get_default_database()
    return db

# Insert data into the MongoDB collection
def user_register(db, data):
    collection = db["Users"]
    try:
        # Attempt to insert the data
        result = collection.insert_one(data)
        # Check if the insert operation was acknowledged (successful)
        return result.acknowledged
    except pymongo.errors.PyMongoError as e:
        # Handle the error (e.g., duplicate key error, connection issue)
        print("Error:", e)
        return False

# Insert data into the MongoDB collection
def user_login(db, data):
    try:
        collection = db["Users"]
        return collection.find_one({"email": data})
    except Exception as e:
        print("Error in login",e)

# Insert data into the MongoDB collection
def insert_data(db, data):
    collection = db["food_items"]
    result = collection.insert_one(data)
    return result.acknowledged

# Retrieve all data from the MongoDB collection
def get_all_data(db):
    collection = db["food_items"]
    return list(collection.find())
