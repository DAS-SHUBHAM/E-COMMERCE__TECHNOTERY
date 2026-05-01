from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.sales_model import Orders
from Models.post_sales_model import OrderTracking

@jwt_required()
def track_order_fn(order_uuid):
    user_id = get_jwt_identity()
    
    order = Orders.query.filter_by(uuid=order_uuid, user_id=user_id).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404

    tracking_updates = OrderTracking.query.filter_by(order_id=order.orders_id).order_by(OrderTracking.created_at.desc()).all()

    return jsonify({
        "order_status": order.status,
        "updates": [{
            "status": t.status,
            "message": t.message,
            "time": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for t in tracking_updates]
    }), 200  