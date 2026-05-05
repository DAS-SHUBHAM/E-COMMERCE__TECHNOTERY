from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.post_sales_model import Wishlist
from Models.product_models import Product

@jwt_required()
def toggle_wishlist_fn(product_id):
    """
    One same API will be responsible to add and remove
    """
    user_id = get_jwt_identity()
    
    # 1. Check if product exists
    product = Product.query.get(product_id)
    if not product or not product.is_active:
        return jsonify({"message": "Product not found or unavailable"}), 404

    # 2. Check if already in wishlist
    existing_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if existing_item:
        # If existing please remove
        db.session.delete(existing_item)
        db.session.commit()
        return jsonify({"message": f"{product.name} removed from wishlist"}), 200
    else:
        # If not then add
        new_item = Wishlist(user_id=user_id, product_id=product_id)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": f"{product.name} added to wishlist"}), 201

@jwt_required()
def get_wishlist_fn():
    """
    User ki poori wishlist dekhne ke liye API
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
                "wishlist_id": item.wishlist_id,
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price
            })
            
    return jsonify({"wishlist": items_data}), 200