from flask import request, jsonify
from extensions import db
from Models.user_models import User, OTP
from datetime import datetime

def verify_otp_fn():
    """
    Handles OTP verification for user/seller accounts.
    Supports edge cases like expired OTPs, already verified accounts, and missing data.
    """
    
    # Extract data from the incoming JSON request
    data = request.get_json()
    email = data.get('email')
    code = data.get('otp_code')

    # 1. Validation: Ensure both required fields are present (400 Bad Request)
    if not email or not code:
        return jsonify({
            "message": "Both email and otp_code are mandatory."
        }), 400

    # 2. Database Check: Verify if the user exists in the system (404 Not Found)
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            "message": "No account associated with this email address."
        }), 404

    # 3. State Check: Prevent re-verification of already active accounts (409 Conflict)
    if user.is_verified:
        return jsonify({
            "message": "This account has already been verified. Please proceed to login."
        }), 409

    # 4. OTP Retrieval: Fetch the most recent unused verification OTP for this user
    otp_record = OTP.query.filter_by(
        user_id=user.user_id, 
        otp_code=code, 
        is_used=False,
        action="verification"
    ).order_by(OTP.created_at.desc()).first()

    # 5. Logic Branching: Differentiate between a 'Wrong OTP' and an 'Expired OTP'
    
    # Case A: OTP not found (either code is wrong or action/status mismatch)
    if not otp_record:
        return jsonify({
            "message": "Invalid OTP. Please check the code and try again."
        }), 400

    # Case B: Correct OTP provided but it has passed its expiration time (410 Gone)
    if otp_record.expires_at < datetime.utcnow():
        return jsonify({
            "message": "This OTP has expired. Please request a new verification code."
        }), 410

    # 6. Finalization: Update database records within a safe transaction block
    try:
        # Mark the user account as active/verified
        user.is_verified = True
        
        # Deactivate the OTP record so it cannot be reused
        otp_record.is_used = True
        
        # Commit changes to the database
        db.session.commit()
        
        return jsonify({
            "message": "Account verified successfully! You are now authorized to login."
        }), 200

    except Exception as e:
        # Rollback the transaction in case of a database crash/error
        db.session.rollback()
        return jsonify({
            "message": "An internal server error occurred while updating status.",
            "error": str(e)
        }), 500