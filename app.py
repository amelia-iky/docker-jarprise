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
mongodb_connect = os.environ.get("MONGO_URI")
database = os.environ.get("DATABASE")
port = int(os.environ.get("PORT"))

# Connect to MongoDB
try:
    # MongoDB
    client = MongoClient(mongodb_connect)

    # Databases
    db = client[database]

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
# Create
@app.route('/product', methods=['POST'])
def createProduct():
    try:
        # Request data
        data = request.get_json()
        # Validate data
        product = ProductModel(**data)
        # Create data
        result = products.insert_one(product.dict())

        # Response
        return jsonify({
            "message": "Data created successfully!",
            "data": product.dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

""" Sales API """
# Create
@app.route('/sale', methods=['POST'])
def createSale():
    try:
        # Request data
        data = request.get_json()
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        # Validate data
        if not product_id or not quantity:
            return jsonify({"error": "Data cannot be empty"}), 400

        if quantity <= 0:
            return jsonify({"error": "Quantity must be greater than 0"}), 400

        # Find product by ID
        product = products.find_one({"_id": ObjectId(product_id)})

        if not product:
            return jsonify({"error": "Data product not found"}), 404

        if product["stock"] < quantity:
            return jsonify({"error": "Stock not enough"}), 400

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
            "message": "Data created successfully!",
            "data": sale
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all
@app.route('/sale', methods=['GET'])
def getAllSale():
    try:
        # Fetch data
        sales_data = list(sales.find())

        # Convert ObjectId to string
        for sale in sales_data:
            sale["_id"] = str(sale["_id"])
            sale["product_id"] = str(sale["product_id"])

        # Response
        return jsonify({
            "message": "Sales retrieved successfully",
            "data": sales_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get by ID
@app.route('/sale/<string:sale_id>', methods=['GET'])
def getOneSale(sale_id):
    try:
        # Find data
        sale = sales.find_one({"_id": ObjectId(sale_id)})

        if not sale:
            return jsonify({"error": "Data sale not found"}), 404

        # Convert ObjectId to string
        sale["_id"] = str(sale["_id"])
        sale["product_id"] = str(sale["product_id"])

        # Response
        return jsonify({
            "message": "Sale retrieved successfully",
            "data": sale
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run app
if __name__ == '__main__':
    app.run(debug=True, port=port)
