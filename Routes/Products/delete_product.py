from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import Product, Specification 
from Models.sales_model import OrderItem 

@jwt_required()
def delete_product_fn(product_uuid):
    """
    Handles the soft deletion of a product and its specifications.
    Prevents deletion if there are active orders linked to the product.
    """
    
    # =======================================================
    # 1. ROLE VALIDATION
    # =======================================================
    claims = get_jwt()
    # Check if the user has the Seller role (Role 2)
    if claims.get('role') != 2: 
        return jsonify({
            "message": "Access Denied! Only sellers are authorized to delete products."
        }), 403

    current_seller_id = int(get_jwt_identity())

    # =======================================================
    # 2. OWNERSHIP & EXISTENCE VALIDATION
    # =======================================================
    # Fetch the product only if it belongs to the seller and is currently active
    product = Product.query.filter_by(
        uuid=product_uuid, 
        seller_id=current_seller_id,
        is_active=True 
    ).first()

    if not product:
        return jsonify({
            "message": "Product not found, already deleted, or you do not have permission to access it."
        }), 404

    # =======================================================
    # 3. ACTIVE ORDERS VALIDATION (Integrity Check)
    # =======================================================
    # Check if there are any orders for this product that are NOT yet completed or cancelled.
    # We define 'Active' as any status other than Delivered, Cancelled, or Returned.
    active_order = OrderItem.query.filter(
        OrderItem.product_id == product.product_id,
        OrderItem.status.notin_(['Delivered', 'Cancelled', 'Returned'])
    ).first()

    if active_order:
        return jsonify({
            "message": "Deletion Blocked! This product is part of an active order. Please complete or cancel all pending orders for this item before deleting."
        }), 400 # 400 Bad Request / Conflict

    # =======================================================
    # 4. APPLY SOFT DELETE (Product + Specifications)
    # =======================================================
    try:
        # Step A: Deactivate the main product record
        product.is_active = False

        # Step B: Deactivate all related specifications to keep data consistent
        Specification.query.filter_by(
            product_id=product.product_id 
        ).update({"is_active": False})

        # Commit all changes as a single transaction
        db.session.commit()

        return jsonify({
            "message": f"Product '{product.name}' and its specifications have been successfully deactivated.",
            "product_uuid": product.uuid
        }), 200

    except Exception as e:
        # Rollback in case of a database error to prevent partial updates
        db.session.rollback()
        return jsonify({
            "message": "An error occurred while trying to delete the product.",
            "error": str(e)
        }), 500