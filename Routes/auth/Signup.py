from flask import request, jsonify
from extensions import db, bcrypt, redis_client  # Imported redis_client
from Models.user_models import User  # Removed OTP model import since it's no longer used
from utils.helpers import generate_uuid, generate_otp, send_otp_email

def signup_fn():
    data = request.get_json()
    email = data.get('email')
    
    # 1. Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    # 2. Hash password securely using Bcrypt
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    try:
        # 3. Create a new unverified User record object
        new_user = User(
            uuid=generate_uuid(),
            username=data.get('username'),
            email=email,
            password=hashed_password,
            role_id=data.get('role_id', 3), # Defaults to 3 (Customer) if not provided
            is_verified=False,
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush() # Secure user instance context and ensure user_id is ready if needed

        # 4. Generate 6-digit verification OTP code
        otp_code = generate_otp()

        # 5. Trigger the HTML email delivery service
        email_sent = send_otp_email(new_user.email, otp_code)
        
        # 6. Finalize database transaction and store verification data in cache if email is sent
        if email_sent:
            # Store OTP in Redis cache with an automated 10-minute (600 seconds) expiration window
            # Using the format key "otp:<email>" for fast execution lookups
            redis_client.setex(f"otp:{email}", 600, otp_code)

            # Commit user records changes safely to MySQL
            db.session.commit()
            
            return jsonify({
                "message": "User registered. Verification code sent to your email.", 
                "user_uuid": new_user.uuid
            }), 201
        else:
            # Cancel database transaction if email distribution channel throws an unexpected fault
            db.session.rollback() 
            return jsonify({
                "message": "Failed to send verification email. Please check your email address or try again later."
            }), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred during signup", "error": str(e)}), 500