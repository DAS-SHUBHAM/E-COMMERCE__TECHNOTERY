from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.sales_model import Orders

@jwt_required()
def get_history_fn():
    user_id = get_jwt_identity()
    orders = Orders.query.filter_by(user_id=user_id).order_by(Orders.created_at.desc()).all()

    return jsonify([{
        "uuid": o.uuid,
        "total_amount": o.total_amount,
        "status": o.status,
        "payment_method": o.payment_method,
        "date": o.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for o in orders]), 200