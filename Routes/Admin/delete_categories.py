from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from Models.product_models import Category, Product 

@jwt_required()
def delete_category_fn(category_uuid):
    claims = get_jwt()
    if claims.get('role') != 1:
        return jsonify({"message": "Access Denied! Only Admin can delete categories."}), 403

    # 1. Check if Category exists and is active
    category = Category.query.filter_by(uuid=category_uuid, is_active=True).first()
    
    if not category:
        return jsonify({"message": "Category not found or already deleted!"}), 404

    #  CHECK FOR LINKED ACTIVE PRODUCTS ---
    # "We are verifying whether there are any active products linked to this specific category_id."
    active_products_exist = Product.query.filter_by(category_id=category.id, is_active=True).first()

    if active_products_exist:
        return jsonify({
            "message": f"Conflict: Cannot delete '{category.name}'. There are active products linked to this category. Please delete or move those products first."
        }), 400 # 400 Bad Request (Data Integrity Conflict)

    # --- SOFT DELETE LOGIC ---
    category.is_active = False 
    db.session.commit()

    return jsonify({
        "message": f"Category '{category.name}' has been soft deleted (deactivated) successfully."
    }), 200