from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.sales_model import Orders
from Models.post_sales_model import OrderTracking
from Models.user_models import User

@jwt_required()
def update_order_status_admin_fn(order_uuid):
    # 1. Security Check: Verify if the logged-in user is an Admin
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)
    
    # SECURITY FIX: Using 'role_id' instead of 'role'
    # Assuming role_id == 1 is for Admin. Please change '1' if your Admin ID is different.
    if not admin_user or admin_user.role_id != 1:
        return jsonify({"message": "Unauthorized. Admin access required."}), 403

    data = request.get_json()
    new_status = data.get('status')  
    custom_message = data.get('message', f"Order status updated to {new_status}")

    # List of allowed status transitions
    allowed_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    if new_status not in allowed_statuses:
        return jsonify({"message": f"Invalid status. Choose from: {', '.join(allowed_statuses)}"}), 400

    # 2. Fetch the Order using UUID
    order = Orders.query.filter_by(uuid=order_uuid).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404

    # 3. Business Logic: Prevent updating a 'cancelled' order
    if order.status == 'cancelled':
        return jsonify({"message": "Cannot update status. This order has already been cancelled."}), 400

    try:
        # 4. Update the Main Order table status
        order.status = new_status
        
        # 5. Create or Update the Tracking entry to keep history in sync
        tracking = OrderTracking.query.filter_by(order_id=order.orders_id).first()
        if tracking:
            tracking.status = new_status
            tracking.message = custom_message
        else:
            # If tracking entry doesn't exist, create a new one
            new_tracking = OrderTracking(
                order_id=order.orders_id,
                status=new_status,
                message=custom_message
            )
            db.session.add(new_tracking)

        # 6. Save changes to the database
        db.session.commit()

        return jsonify({
            "message": f"Order status successfully updated to {new_status}",
            "order_uuid": order_uuid,
            "current_status": order.status
        }), 200

    except Exception as e:
        # Rollback in case of database failure
        db.session.rollback()
        return jsonify({"message": "Failed to update status", "error": str(e)}), 500