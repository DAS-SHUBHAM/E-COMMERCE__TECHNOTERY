from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import Product

@jwt_required()
def update_product_fn(product_uuid):
    # =======================================================
    # 1. ROLE VALIDATION: Check if the user is a Seller
    # =======================================================
    claims = get_jwt()
    if claims.get('role') != 2: 
        return jsonify({"message": "Access Denied! Only sellers can update products."}), 403

    current_seller_id = int(get_jwt_identity())

    # =======================================================
    # 2. OWNERSHIP VALIDATION: Check if product exists AND belongs to this seller
    # =======================================================
    product = Product.query.filter_by(
        uuid=product_uuid, 
        seller_id=current_seller_id, # <--- The crucial security lock!
        is_active=True
    ).first()

    if not product:
        return jsonify({"message": "Product not found or you do not have permission to edit it."}), 404

    # =======================================================
    # 3. APPLY UPDATES
    # =======================================================
    # We use get_json() assuming the frontend will send a clean JSON object for text updates
    data = request.get_json()
    if not data:
         return jsonify({"message": "No data provided for update"}), 400

    try:
        # Only update the fields that the seller actually sent in the request
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = float(data['price'])
        if 'stock' in data:
            product.stock = int(data['stock'])
   
        db.session.commit()

        return jsonify({
            "message": "Product updated successfully!",
            "product_uuid": product.uuid
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update product", "error": str(e)}), 500