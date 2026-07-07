from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import SellerCategory # Assuming Category model is also in the same file

def approve_seller_category_fn(request_uuid):
    """
    Allows Admin to approve a seller's category request.
    Prevents duplicate approvals and handles missing requests.
    """
    
    # 1. Permission Check: Verify if the user is an Admin (Role 1)
    claims = get_jwt()
    if claims.get('role') != 1: 
        return jsonify({
            "message": "Access Denied! Only Admin can approve category requests."
        }), 403

    # 2. Extract Admin Identity and Optional Body Data
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}
    admin_note = data.get('admin_note', "Approved by Admin")

    # 3. Find the Request: Locate the category request by its UUID
    category_req = SellerCategory.query.filter_by(uuid=request_uuid).first()
    
    if not category_req:
        return jsonify({
            "message": "Category request not found. Please verify the UUID."
        }), 404

    # 4. Conflict Check: Prevent re-processing an already approved request (400 Bad Request)
    if category_req.is_approved:
        return jsonify({
            "message": "Conflict: This category request has already been approved."
        }), 400

    # 5. Process Approval
    try:
        # Mark as approved and log who did it
        category_req.is_approved = True
        category_req.is_active = True  # FIX: Isko active karna zaroori hai taaki seller is category me products add kar sake
        category_req.updated_by = admin_id
        
        # Optional: If your model has a field for notes, update it here
        # category_req.admin_comments = admin_note 

        db.session.commit()

        # FIX: Hata diya category_req.category_name kyunki ye attribute model me nahi hai.
        # Agar category ka naam dikhana hi hai, toh category_id use kar sakte hain.
        return jsonify({
            "message": f"Category request for Category ID '{category_req.category_id}' has been approved successfully!"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Internal Server Error during approval process.",
            "error": str(e)
        }), 500