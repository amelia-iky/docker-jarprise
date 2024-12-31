import os
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# APP
app = Flask(__name__)

# ENVIRONMENT VARIABLES
mongodb_connect = os.environ.get("MONGO_URI")
database = os.environ.get("DATABASE")
port = int(os.environ.get("PORT"))

# DATABASE CONNECTION
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

# MODELS
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

# API
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

# Get all
@app.route('/product', methods=['GET'])
def getAllProduct():
    try:
        # Fetch data
        data = list(products.find())
        
        # Convert ObjectId to string
        for product in data:
            product["_id"] = str(product["_id"])

        # Response
        return jsonify({
            "message": "Products retrieved successfully!",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get by ID
@app.route('/product/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        # Find data
        data = products.find_one({"_id": ObjectId(product_id)})

        if not data:
            return jsonify({"error": "Data product not found"}), 404

        # Convert ObjectId to string
        data["_id"] = str(data["_id"])

        # Response
        return jsonify({
            "message": "Product retrieved successfully!",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete all
@app.route('/product', methods=['DELETE'])
def deleteAllProduct():
    try:
        # Delete all products
        data = products.delete_many({})

        # Response
        return jsonify({
            "message": f"{data.deleted_count} data deleted successfully!"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete by ID
@app.route('/product/<string:product_id>', methods=['DELETE'])
def deleteOneProduct(product_id):
    try:
        # Delete data
        data = products.delete_one({"_id": ObjectId(product_id)})

        # Check if data exists
        if data.deleted_count == 0:
            return jsonify({"error": "Data product not found"}), 404

        # Response
        return jsonify({
            "message": "Data deleted successfully!"
        }), 200

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
        data = list(sales.find())

        # Convert ObjectId to string
        for sale in data:
            sale["_id"] = str(sale["_id"])
            sale["product_id"] = str(sale["product_id"])

        # Response
        return jsonify({
            "message": "Sales retrieved successfully",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get by ID
@app.route('/sale/<string:sale_id>', methods=['GET'])
def getOneSale(sale_id):
    try:
        # Find data
        data = sales.find_one({"_id": ObjectId(sale_id)})

        if not data:
            return jsonify({"error": "Data sale not found"}), 404

        # Convert ObjectId to string
        data["_id"] = str(data["_id"])
        data["product_id"] = str(data["product_id"])

        # Response
        return jsonify({
            "message": "Sale retrieved successfully",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RUN APP
if __name__ == '__main__':
    app.run(debug=True, port=port)
