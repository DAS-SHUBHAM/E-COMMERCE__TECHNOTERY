from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
import uuid

from Models.post_sales_model import Wishlist
from Models.product_models import Product

@jwt_required()
def toggle_wishlist_fn(product_uuid): # Yahan id ki jagah uuid kar diya
    user_id = get_jwt_identity()
    
    # 1. Find the product using its uuid
    product = Product.query.filter_by(uuid=product_uuid).first()
    if not product or not product.is_active:
        return jsonify({"message": "Product not found or unavailable"}), 404

    # 2. Database relation  product.product_id used
    existing_item = Wishlist.query.filter_by(user_id=user_id, product_id=product.product_id).first()
    
    if existing_item:
        db.session.delete(existing_item)
        db.session.commit()
        return jsonify({"message": f"{product.name} removed from wishlist"}), 200
    else:
        new_item = Wishlist(
            uuid=str(uuid.uuid4()), #generated new uuid
            user_id=user_id, 
            product_id=product.product_id
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": f"{product.name} added to wishlist"}), 201

# get_wishlist_fn mein item.wishlist_id ki jagah item.uuid return karwa sakte hain
@jwt_required()
def get_wishlist_fn():
    """
    User ki poori wishlist dekhne ke liye API (Updated with UUID)
    """
    user_id = get_jwt_identity()
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
    
    if not wishlist_items:
        return jsonify({"message": "Your wishlist is empty", "wishlist": []}), 200
        
    items_data = []
    for item in wishlist_items:
        product = Product.query.get(item.product_id)
        if product:
            items_data.append({
                "wishlist_uuid": item.uuid,     # Ab id ki jagah uuid aayega
                "product_uuid": product.uuid,   # Product ka bhi uuid
                "name": product.name,
                "price": product.price
            })
            
    return jsonify({"wishlist": items_data}), 200