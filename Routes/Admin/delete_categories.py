from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from Models.product_models import Category

def delete_category_fn(category_uuid):
    claims = get_jwt()
    if claims.get('role') != 1:
        return jsonify({"message": "Access Denied! Only Admin can delete categories."}), 403

    # Searching for is active=true
    category = Category.query.filter_by(uuid=category_uuid, is_active=True).first()
    
    if not category:
        return jsonify({"message": "Category not found or already deleted!"}), 404

    # ---  SOFT DELETE LOGIC ---
    category.is_active = False  # Category ab inactive ho gayi hai
    db.session.commit()

    return jsonify({
        "message": f"Category '{category.name}' has been soft deleted (deactivated) successfully."
    }), 200