from flask import request, jsonify
from extensions import db, bcrypt
from Models.user_models import User, OTP
from datetime import datetime, timedelta
from utils.helpers import generate_uuid, generate_otp, send_otp_email


def signup_fn():
    data = request.get_json()
    
    # 1. Check if user already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Email already registered"}), 400

    # 2. Hash password
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    try:
        # 3. Create User object
        new_user = User(
            uuid=generate_uuid(),
            username=data.get('username'),
            email=data.get('email'),
            password=hashed_password,
            role_id=data.get('role_id', 3), # Defaults to 3 (Customer) if not provided
            is_verified=False,
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush() # Get user_id before commit for the OTP record

        # 4. Generate 6-digit OTP using your helper
        otp_code = generate_otp()
        new_otp = OTP(
            uuid=generate_uuid(),
            user_id=new_user.user_id,
            otp_code=otp_code,
            action="verification",
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(new_otp)

        # 5. Trigger the HTML email function
        email_sent = send_otp_email(new_user.email, otp_code)
        
        # 6. Finalize transaction based on email success
        if email_sent:
            db.session.commit()
            return jsonify({
                "message": "User registered. Verification code sent to your email.", 
                "user_uuid": new_user.uuid
            }), 201
        else:
            db.session.rollback() # Cancel the DB insertion if email fails
            return jsonify({
                "message": "Failed to send verification email. Please check your email address or try again later."
            }), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred during signup", "error": str(e)}), 500