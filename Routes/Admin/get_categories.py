from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from Models.product_models import Category

def get_all_categories_fn():
    # 1. Check if user is Admin
    claims = get_jwt()
    if claims.get('role') != 1:
        return jsonify({"message": "Access Denied! Only Admin can view this."}), 403

    # 2. Fetch all categories from database
    categories = Category.query.filter_by(is_active=True).all()
    
    # 3. Format the data
    category_list = []
    for cat in categories:
        category_list.append({
            "category_id": cat.category_id,
            "uuid": cat.uuid,
            "name": cat.name,
            "description": cat.description
        })

    return jsonify({
        "total_categories": len(category_list),
        "categories": category_list
    }), 200