import os
from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Create a Flask app
app = Flask(__name__)

# Environment variables
mongodb_connection = os.environ.get("MONGO_URI", "mongodb://localhost:27017/db_phone")
port = int(os.environ.get("PORT", 3000))

# Connect to MongoDB with error handling
try:
    client = MongoClient(mongodb_connection)
    print("Server is running on port {}!".format(port))
except Exception as e:
    print(f"Server failed to start: {e}")
    exit(1)

# Basic health check endpoint
@app.route('/')
def index():
    return jsonify({"message": "App is running!"}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=port)
