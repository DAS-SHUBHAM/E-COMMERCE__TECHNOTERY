from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import SellerCategory

def approve_seller_category_fn(request_uuid):
    claims = get_jwt()
    if claims.get('role') != 1:  # 1 = Admin
        return jsonify({"message": "Only Admin can approve categories."}), 403

    admin_id = int(get_jwt_identity())
    
    category_req = SellerCategory.query.filter_by(uuid=request_uuid).first()
    if not category_req:
        return jsonify({"message": "Category request not found"}), 404

    category_req.is_approved = True
    category_req.updated_by = admin_id
    db.session.commit()

    return jsonify({"message": "Seller category approved successfully!"}), 200