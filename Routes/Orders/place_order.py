from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.sales_model import Orders, OrderItem, CartItem
from Models.product_models import Product
from Models.user_models import Address
from Models.post_sales_model import OrderTracking
import uuid

@jwt_required()
def place_order_fn():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    address_uuid = data.get('address_uuid')
    payment_method = data.get('payment_method') # e.g., 'cod', 'upi', 'card', 'net-banking'

    # 1. Validate Shipping Address
    address = Address.query.filter_by(uuid=address_uuid, user_id=user_id).first()
    if not address:
        return jsonify({"message": "Invalid shipping address"}), 400

    # 2. Fetch all active items from the user's cart
    cart_items = CartItem.query.filter_by(user_id=user_id, is_active=True).all()
    if not cart_items:
        return jsonify({"message": "Your cart is empty"}), 400

    try:
        total_amount = 0
        order_items_to_create = []

        # 3. Process each cart item for stock verification and price snapshot
        for item in cart_items:
            # Fetch the product with a 'with_for_update' lock to prevent race conditions during concurrent checkouts
            product = Product.query.with_for_update().get(item.product_id)
            
            if not product or not product.is_active:
                return jsonify({"message": f"Product {product.name if product else 'Unknown'} is no longer available"}), 400

            # Dynamic Stock Check: Final validation before deducting stock
            if product.stock < item.quantity:
                return jsonify({
                    "message": f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {item.quantity}"
                }), 400
            
            # Deduct the quantity from actual stock now that order is being placed
            product.stock -= item.quantity
            
            # Calculate item total based on current price
            item_total = product.price * item.quantity
            total_amount += item_total

            # Prepare OrderItem object (to be linked after the main Order is created)
            order_items_to_create.append(OrderItem(
                uuid=str(uuid.uuid4()),
                product_id=product.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price,
                is_active=True # Setting active for the new order record
            ))

        # 4. Determine Initial Status based on Payment Method
        # Default to 'pending' for online payments until Razorpay verification is successful
        initial_status = 'pending'
        tracking_message = "Order created. Please proceed to complete the payment."

        # If COD, the order is confirmed immediately and ready for processing
        if payment_method and payment_method.lower() == 'cod':
            initial_status = 'processing'
            tracking_message = "Order placed successfully via Cash on Delivery. Awaiting shipment."

        # 5. Create the main Order record
        new_order = Orders(
            uuid=str(uuid.uuid4()),
            user_id=user_id,
            address_id=address.address_id,
            total_amount=total_amount,
            payment_method=payment_method,
            status=initial_status, # Applied dynamic status
            is_active=True
        )
        db.session.add(new_order)
        
        # Flush to generate the orders_id for the primary key relationship without committing
        db.session.flush() 

        # 6. Link prepared items to the Order and initialize Tracking
        for oi in order_items_to_create:
            oi.order_id = new_order.orders_id
            db.session.add(oi)

        # Create tracking entry for the new order
        tracking = OrderTracking(
            order_id=new_order.orders_id,
            status=initial_status, # Applied dynamic status
            message=tracking_message # Applied dynamic message
        )
        db.session.add(tracking)

        # 7. Clear the Cart (Soft Delete)
        # All items currently in cart for this user are marked inactive
        CartItem.query.filter_by(user_id=user_id, is_active=True).update({"is_active": False})

        # 8. Final Commit to Database
        db.session.commit()
        
        # Return different messages depending on the payment method to guide the frontend
        return jsonify({
            "message": tracking_message, 
            "order_uuid": new_order.uuid,
            "total_paid": total_amount,
            "payment_method": payment_method,
            "status": initial_status
        }), 201

    except Exception as e:
        # Rollback all changes (including stock deduction) if any error occurs
        db.session.rollback()
        return jsonify({
            "message": "An error occurred during checkout", 
            "error": str(e)
        }), 500