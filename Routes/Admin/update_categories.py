from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from Models.product_models import Category

def update_category_fn(category_uuid):
    # 1. Check if user is Admin
    claims = get_jwt()
    if claims.get('role') != 1:
        return jsonify({"message": "Access Denied! Only Admin can update categories."}), 403

    # 2. Find the category by UUID
    category = Category.query.filter_by(uuid=category_uuid).first()
    if not category:
        return jsonify({"message": "Category not found!"}), 404

    # 3. Get new data from request
    data = request.get_json()
    new_name = data.get('name')
    new_desc = data.get('description')

    # 4. Update the fields if provided
    if new_name:
        # Check if new name already exists in another category
        existing = Category.query.filter_by(name=new_name).first()
        if existing and existing.uuid != category_uuid:
            return jsonify({"message": f"Category name '{new_name}' is already taken!"}), 400
        category.name = new_name
        
    if new_desc is not None:
        category.description = new_desc

    # 5. Save to database
    db.session.commit()

    return jsonify({
        "message": "Category updated successfully!",
        "category_id": category.category_id,
        "name": category.name
    }), 200