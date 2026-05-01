from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.product_models import Product, ProductImage, Specification

@jwt_required()
def get_details_fn(product_uuid):
    # 1. Get the currently logged-in seller's ID from the token
    current_seller_id = get_jwt_identity()

    # 2. Fetch the product AND ensure the seller_id matches
    product = Product.query.filter_by(
        uuid=product_uuid, 
        seller_id=current_seller_id, # <--- SECURITY CHECK ADDED HERE
        is_active=True
    ).first()
    
    if not product:
        # Changed the message slightly so it covers both missing products and unauthorized access
        return jsonify({"message": "Product not found or access denied"}), 404

    # Fetch related images and specs using the IDs
    images = ProductImage.query.filter_by(product_id=product.product_id, is_active=True).all()
    specs = Specification.query.filter_by(product_id=product.product_id, is_active=True).all()

    return jsonify({
        "uuid": product.uuid,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "images": [img.image_url for img in images],
        "specifications": {s.spec_key: s.spec_value for s in specs}
    }), 200