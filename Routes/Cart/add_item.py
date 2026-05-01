from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.sales_model import CartItem
from Models.product_models import Product
import uuid

@jwt_required()
def add_item_fn():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    product_uuid = data.get('product_uuid')
    quantity_to_add = data.get('quantity', 1)

    # 1. Validate Product existence and check if it is active
    product = Product.query.filter_by(uuid=product_uuid, is_active=True).first()
    if not product:
        return jsonify({"message": "Product not found or currently unavailable"}), 404

    # 2. Check if item already exists in user's cart (even if soft-deleted)
    existing_item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=product.product_id
    ).first()

    # 3. Calculate current quantity in cart
    # If item exists and is_active is 1, take its quantity. Otherwise, it's 0.
    current_cart_quantity = existing_item.quantity if existing_item and existing_item.is_active else 0
    
    # Calculate what the total would be if we allow this addition
    projected_total_quantity = current_cart_quantity + quantity_to_add

    # 4. Dynamic Stock Validation
    # We do NOT subtract from stock here. We only compare the cart request against available stock.
    if projected_total_quantity > product.stock:
        available_to_add = product.stock - current_cart_quantity
        
        if available_to_add <= 0:
            return jsonify({
                "message": f"Maximum stock reached. You already have all {product.stock} available units in your cart."
            }), 400
        
        return jsonify({
            "message": f"Cannot add {quantity_to_add} more. Only {available_to_add} units available to add based on current stock."
        }), 400

    # 5. Add or Update Cart logic
    if existing_item:
        # Update existing record and ensure it's marked as active (revive if it was is_active=0)
        existing_item.quantity = projected_total_quantity
        existing_item.is_active = True 
    else:
        # Create a new cart entry if it doesn't exist
        new_cart_item = CartItem(
            uuid=str(uuid.uuid4()),
            user_id=user_id,
            product_id=product.product_id,
            quantity=quantity_to_add,
            is_active=True
        )
        db.session.add(new_cart_item)

    # 6. Commit changes
    # Note: Product stock is NOT modified here. It remains untouched until Place Order.
    try:
        db.session.commit()
        return jsonify({
            "message": "Item added to cart successfully",
            "total_in_cart": projected_total_quantity,
            "available_stock_reference": product.stock  # Shows total stock without reducing it
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to add to cart", "error": str(e)}), 500