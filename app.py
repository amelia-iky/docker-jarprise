import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId, json_util

load_dotenv()

# Flask app initialization
app = Flask(__name__)

# Get MongoDB URI and database name from environment variables
mongodb_connection = os.environ.get("MONGO_URI", "mongodb://localhost:27017/db_phone")
port = os.environ.get("PORT", "3000")

# Connect to MongoDB
print(f'Connecting to MongoDB at {mongodb_connection}...')
client = MongoClient(mongodb_connection)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
