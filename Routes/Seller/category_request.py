from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import SellerCategory

def request_category_approval_fn():
    claims = get_jwt()
    if claims.get('role') != 2:  # 2 = Seller
        return jsonify({"message": "Only sellers can request category approval"}), 403

    seller_id = int(get_jwt_identity())
    data = request.get_json()
    category_id = data.get('category_id')

    if not category_id:
        return jsonify({"message": "Category ID is required"}), 400

    existing_req = SellerCategory.query.filter_by(seller_id=seller_id, category_id=category_id).first()
    if existing_req:
        if existing_req.is_approved:
            return jsonify({"message": "You are already approved for this category!"}), 400
        return jsonify({"message": "Your request is already pending."}), 400

    new_request = SellerCategory(
        seller_id=seller_id,
        category_id=category_id,
        created_by=seller_id
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Approval request sent to Admin.", "uuid": new_request.uuid}), 201