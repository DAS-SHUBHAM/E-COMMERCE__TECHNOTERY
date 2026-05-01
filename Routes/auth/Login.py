from flask import request, jsonify
from flask_jwt_extended import create_access_token
from extensions import bcrypt
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

        # 4. Enforce OTP Verification
        if not user.is_verified:
            return jsonify({"message": "Please verify your account first"}), 403

        # 5. Enforce Admin Controls
        if not user.is_active:
            return jsonify({"message": "Account is disabled. Contact Admin."}), 403

        # 6. Generate JWT with Identity and Role Claims
        access_token = create_access_token(
            identity=str(user.user_id), 
            additional_claims={"role": user.role_id}
        )

        # 7. Return payload
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