import os
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Flask app
app = Flask(__name__)

# Environment variables
mongodb_connection = os.environ.get("MONGO_URI", "mongodb://localhost:27017/db_phone")
port = int(os.environ.get("PORT", 3000))

# Connect to MongoDB
try:
    client = MongoClient(mongodb_connection)

    # Databases
    db = client["db_phone"]

    # Collections
    products = db["products"]
    sales = db["sales"]

    # Start server
    print("Server is running on port {}!".format(port))
except Exception as e:
    print(f"Server failed to start: {e}")
    exit(1)

# Models
""" Product model """
class ProductModel(BaseModel):
    name: str = Field(...)
    brand: str = Field(...)
    stock: int = Field(...)
    price: float = Field(...)

""" Sale model """
class SaleModel(BaseModel):
    total_product: int = Field(...)
    total_price: float = Field(...)

# Endpoints
""" Testing API """
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello, World!"}), 200

""" Products API """
@app.route('/product', methods=['POST'])
def create_product():
    try:
        # Request data
        data = request.get_json()
        # Validate data
        product = ProductModel(**data)
        # Create data
        result = products.insert_one(product.dict())

        # Response
        return jsonify({
            "message": "Product added successfully!",
            "data": product.dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


""" Sales API """
@app.route('/sale', methods=['POST'])
def create_sale():
    try:
        # Request data
        data = request.get_json()
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        # Validate data
        if not product_id or not quantity:
            return jsonify({"error": "product_id and quantity are required"}), 400

        if quantity <= 0:
            return jsonify({"error": "quantity must be greater than 0"}), 400

        # Find product by ID
        product = products.find_one({"_id": ObjectId(product_id)})

        if not product:
            return jsonify({"error": "Product not found"}), 404

        if product["stock"] < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        # Set total price
        total_price = product["price"] * quantity

        # Update stock product
        products.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"stock": -quantity}}
        )

        # Create data
        sale = {
            "product_id": product_id,
            "total_product": quantity,
            "total_price": total_price,
        }

        # Save data
        result = sales.insert_one(sale)

        # Set ID to objectID
        sale["_id"] = str(result.inserted_id)

        # Response
        return jsonify({
            "message": "Sale added successfully",
            "data": sale
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=port)
