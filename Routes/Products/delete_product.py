from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import Product
from Models.product_models import Specification 

@jwt_required()
def delete_product_fn(product_uuid):
    # =======================================================
    # 1. ROLE VALIDATION
    # =======================================================
    claims = get_jwt()
    if claims.get('role') != 2: 
        return jsonify({"message": "Access Denied! Only sellers can delete products."}), 403

    current_seller_id = int(get_jwt_identity())

    # =======================================================
    # 2. OWNERSHIP & EXISTENCE VALIDATION
    # =======================================================
    product = Product.query.filter_by(
        uuid=product_uuid, 
        seller_id=current_seller_id,
        is_active=True 
    ).first()

    if not product:
        return jsonify({"message": "Product not found, already deleted, or access denied."}), 404

    # =======================================================
    # 3. APPLY SOFT DELETE (Product + Specifications)
    # =======================================================
    try:
        # Soft delete the product
        product.is_active = False

        # Soft delete all related specifications using the shared product_id FK
        Specification.query.filter_by(
            product_id=product.product_id  # ✅ product_id is PK in product, FK in specification
        ).update({"is_active": False})

        db.session.commit()

        return jsonify({
            "message": "Product deleted successfully",
            "product_uuid": product.uuid
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete product", "error": str(e)}), 500