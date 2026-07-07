from flask import request, jsonify
from extensions import db, redis_client  # Imported redis_client for caching layer
from Models.user_models import User  # Removed OTP table import since it is replaced by Redis

def verify_otp_fn():
    """
    Handles OTP verification for user/seller accounts using Redis.
    Supports edge cases like expired OTPs, already verified accounts, and missing data.
    """
    try:
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

        # 4. OTP Retrieval: Extract the cached verification token directly from Redis memory
        cached_otp = redis_client.get(f"otp:{email}")

        # 5. Logic Branching: Evaluate missing, wrong, or expired states
        # If the key does not exist, it means the 10-minute TTL expired (410 Gone)
        if not cached_otp:
            return jsonify({
                "message": "This OTP has expired or does not exist. Please request a new verification code."
            }), 410

        # If the key exists but does not match the user's input parameter (400 Bad Request)
        if cached_otp != str(code):
            return jsonify({
                "message": "Invalid OTP. Please check the code and try again."
            }), 400

        # 6. Finalization: Update database records within a safe transaction block
        # Mark the user account as active/verified
        user.is_verified = True
        
        # Instantly remove the token key from Redis to prevent duplicate multi-pass replay attempts
        redis_client.delete(f"otp:{email}")
        
        # Commit the state modification to the primary MySQL engine
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