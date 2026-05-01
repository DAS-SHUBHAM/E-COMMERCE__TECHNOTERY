from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import Category

def create_category_fn():
    # 1. Only Admin Allowed
    claims = get_jwt()
    if claims.get('role') != 1:  # 1 = Admin
        return jsonify({"message": "Only Admin can create new categories."}), 403

    admin_id = int(get_jwt_identity())
    data = request.get_json()

    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({"message": "Category name is required"}), 400

    # 2. Check if category exists
    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"message": f"Category '{name}' already exists!"}), 400

    # 3. Create New Category
    new_category = Category(
        name=name,
        description=description,
        created_by=admin_id
    )
    
    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        "message": "Category created successfully!",
        "category_id": new_category.category_id, 
        "category_name": new_category.name,
        "uuid": new_category.uuid   
    }), 201