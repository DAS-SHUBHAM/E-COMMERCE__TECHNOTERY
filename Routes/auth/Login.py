from flask import request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db, bcrypt, redis_client  # Imported db and redis_client
from Models.user_models import User

def login_fn():
    try:
        data = request.get_json()
        
        # 1. Validate input payload
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"message": "Email and password are required"}), 400

        # 2. Find the user by email
        user = User.query.filter_by(email=data.get('email')).first()

        # 3. Verify credentials
        if not user or not bcrypt.check_password_hash(user.password, data.get('password')):
            return jsonify({"message": "Invalid email or password"}), 401

        # 4. Enforce OTP Verification status check
        if not user.is_verified:
            return jsonify({"message": "Please verify your account first"}), 403

        # 5. Enforce Admin Controls (Account Suspension check)
        if not user.is_active:
            return jsonify({"message": "Account is disabled. Contact Admin."}), 403

        # 6. Generate JWT with Identity and Role Claims
        access_token = create_access_token(
            identity=str(user.user_id), 
            additional_claims={"role": user.role_id}
        )

        # 7. Return user payload data along with access token
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "uuid": user.uuid,
                "username": user.username,
                "role_id": user.role_id,
                "is_verified": user.is_verified
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500


def verify_otp_fn():
    """
    Handles account activation by verifying the 6-digit OTP code stored inside the Redis memory engine.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        otp_input = data.get('otp')

        # 1. Validate input payload fields
        if not email or not otp_input:
            return jsonify({"message": "Email and OTP code are required"}), 400

        # 2. Verify if the target user profile exists within the primary system
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User configuration not found"}), 404

        # 3. Extract cached OTP record directly from Redis memory structure
        cached_otp = redis_client.get(f"otp:{email}")

        # 4. Perform match evaluation and validate expiration constraints
        if not cached_otp or cached_otp != str(otp_input):
            return jsonify({"message": "Invalid or expired OTP code"}), 401

        # 5. Update user verification flags upon validation match success
        user.is_verified = True
        
        # 6. Delete the validated OTP cache key instantly to prevent multi-pass replay attacks
        redis_client.delete(f"otp:{email}")
        
        # 7. Commit changes persistently to MySQL engine layer
        db.session.commit()

        # 8. Return successful verification feedback payload
        return jsonify({"message": "Account verified and activated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred during OTP verification", "error": str(e)}), 500