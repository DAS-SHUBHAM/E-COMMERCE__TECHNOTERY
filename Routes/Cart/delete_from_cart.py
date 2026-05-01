# Routes/Cart/delete_item.py

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.sales_model import CartItem

@jwt_required()
def delete_item_fn():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    cart_item_uuid = data.get('cart_item_uuid')

    # =======================================================
    # 1. INPUT VALIDATION
    # =======================================================
    if not cart_item_uuid:
        return jsonify({"message": "cart_item_uuid is required"}), 400

    # =======================================================
    # 2. OWNERSHIP & EXISTENCE VALIDATION
    # =======================================================
    # Ensure the cart item exists, belongs to this user, and is currently active
    cart_item = CartItem.query.filter_by(
        uuid=cart_item_uuid,
        user_id=user_id,
        is_active=True
    ).first()

    if not cart_item:
        return jsonify({"message": "Cart item not found, already removed, or access denied."}), 404

    # =======================================================
    # 3. SOFT DELETE
    # =======================================================
    try:
        cart_item.is_active = False

        db.session.commit()

        return jsonify({"message": "Item removed from cart successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to remove cart item", "error": str(e)}), 500