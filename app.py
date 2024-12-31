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

# ENDPOINTS API
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

@app.route('/product/<string:product_id>', methods=['PUT'])
def updateProduct(product_id):
    try:
        # Request data
        data = request.get_json()

        # Find data is exists
        existing_product = products.find_one({"_id": ObjectId(product_id)})
        if not existing_product:
            return jsonify({"error": "Product not found"}), 404

        # Merge existing product data with the updated fields
        updated_data = {**existing_product, **data}
        updated_data["_id"] = str(existing_product["_id"])

        # Validate data
        product = ProductModel(**updated_data)

        # Update data
        products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": product.dict()}
        )

        # Response
        return jsonify({
            "message": "Data updated successfully!",
            "data": product.dict()
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

@app.route('/sale/<string:sale_id>', methods=['PUT'])
def updateSale(sale_id):
    try:
        # Request data
        data = request.get_json()
        new_product_id = data.get("product_id")
        new_quantity = data.get("quantity")

        # Validate request data
        if not new_product_id or not new_quantity:
            return jsonify({"error": "product_id and quantity are required"}), 400

        if new_quantity <= 0:
            return jsonify({"error": "Quantity must be greater than 0"}), 400

        # Find the existing sale
        existing_sale = sales.find_one({"_id": ObjectId(sale_id)})
        if not existing_sale:
            return jsonify({"error": "Sale data not found"}), 404

        # Find the old product associated with the sale
        old_product = products.find_one({"_id": ObjectId(existing_sale["product_id"])})
        if not old_product:
            return jsonify({"error": "Old product data not found"}), 404

        # Restore the stock of the old product
        products.update_one(
            {"_id": ObjectId(existing_sale["product_id"])},
            {"$inc": {"stock": existing_sale["total_product"]}}
        )

        # Find the new product
        new_product = products.find_one({"_id": ObjectId(new_product_id)})
        if not new_product:
            return jsonify({"error": "New product data not found"}), 404

        if new_product["stock"] < new_quantity:
            return jsonify({"error": "Insufficient stock for the new product"}), 400

        # Deduct the stock of the new product
        products.update_one(
            {"_id": ObjectId(new_product_id)},
            {"$inc": {"stock": -new_quantity}}
        )

        # Calculate the new total price
        new_total_price = new_product["price"] * new_quantity

        # Update the sale data
        updated_sale = {
            "product_id": new_product_id,
            "total_product": new_quantity,
            "total_price": new_total_price
        }

        sales.update_one(
            {"_id": ObjectId(sale_id)},
            {"$set": updated_sale}
        )

        # Prepare the response data
        updated_sale["_id"] = sale_id
        updated_sale["product_id"] = new_product_id

        # Response
        return jsonify({
            "message": "Sale updated successfully!",
            "data": updated_sale
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RUN APP
if __name__ == '__main__':
    app.run(debug=True, port=port)
