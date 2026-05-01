from flask import jsonify
from extensions import db
from Models.product_models import SellerCategory 
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def get_my_requests_fn():
    current_seller_id = get_jwt_identity()
    
    my_requests = SellerCategory.query.filter_by(seller_id=current_seller_id).all()
    
    response_data = []
    for item in my_requests:
        response_data.append({
            "category_id": item.category_id, 
            "status": "Approved" if item.is_approved else "Pending"
        })
        
    return jsonify({
        "message": "My category requests fetched successfully",
        "total_requests": len(response_data),
        "requests": response_data
    }), 200