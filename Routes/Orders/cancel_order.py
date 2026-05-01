from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.sales_model import OrderItem, Orders
from Models.product_models import Product
from Models.post_sales_model import OrderTracking 

@jwt_required()
def cancel_order_item_fn(order_item_uuid):
    user_id = get_jwt_identity()

    # 1. Fetch OrderItem and verify ownership
    order_item = db.session.query(OrderItem).join(
        Orders, OrderItem.order_id == Orders.orders_id
    ).filter(
        OrderItem.uuid == order_item_uuid,
        Orders.user_id == user_id,
        OrderItem.is_active == True
    ).first()

    if not order_item:
        return jsonify({"message": "Order item not found or already cancelled"}), 404

    try:
        # 2. Restore Stock
        product = Product.query.with_for_update().get(order_item.product_id)
        if product:
            product.stock += order_item.quantity

        # 3. Mark the individual item as inactive
        order_item.is_active = False
        db.session.flush()

        # 4. Update the tracking status for this specific cancellation
        # We find the tracking entry for this order and update its status
        tracking = OrderTracking.query.filter_by(order_id=order_item.order_id).first()
        if tracking:
            tracking.status = 'cancelled'
            tracking.message = "Order was cancelled by the user. Stock restored."

        # 5. Check if any other active items exist in the same order
        remaining_active_items = OrderItem.query.filter(
            OrderItem.order_id == order_item.order_id,
            OrderItem.is_active == True
        ).first()

        # 6. If NO active items left, update the main Order status to 'cancelled'
        if not remaining_active_items:
            main_order = Orders.query.get(order_item.order_id)
            if main_order:
                main_order.is_active = False
                main_order.status = 'cancelled' 

        db.session.commit()

        return jsonify({
            "message": "Order cancelled successfully and status updated to 'cancelled'.",
            "order_item_uuid": order_item_uuid
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Cancellation failed", "error": str(e)}), 500