from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.sales_model import CartItem
from Models.product_models import Product

@jwt_required()
def view_cart_fn():
    # 1. Securely retrieve the logged-in user's identity (ID) from the JWT token
    user_id = get_jwt_identity()

    # 2. Perform a Join query to get both Cart details and Product details in one go.
    # We filter by user_id to ensure a user can only see their own cart items.
    # We also check for is_active=True because checked-out items are marked False (0).
    cart_items = db.session.query(CartItem, Product).join(
        Product, CartItem.product_id == Product.product_id
    ).filter(
        CartItem.user_id == user_id,
        CartItem.is_active == True
    ).all()

    # 3. Handle Empty Cart Scenario
    # If no active items are found, return a success response with zeroed values.
    if not cart_items:
        return jsonify({
            "message": "Your cart is currently empty",
            "cart": [],
            "total_items": 0,
            "cart_total": 0
        }), 200

    output = []
    cart_total = 0.0

    # 4. Loop through the results to calculate totals and format the response
    for item, product in cart_items:
        # Calculate individual item total (Price * Quantity)
        item_total = product.price * item.quantity
        cart_total += item_total
        
        output.append({
            "cart_item_uuid": item.uuid,
            "product_name": product.name,
            "product_uuid": product.uuid,
            "price": product.price,
            "quantity": item.quantity,
            "item_total": item_total,
            "stock_status": "In Stock" if product.stock > 0 else "Out of Stock"
        })

    # 5. Return the full cart details
    return jsonify({
        "status": "success",
        "cart": output,
        "total_items": len(output),
        "cart_total": cart_total
    }), 200