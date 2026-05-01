from flask import request, jsonify
from extensions import db
from Models.user_models import User, OTP
from datetime import datetime

def verify_otp_fn():
    data = request.get_json()
    email = data.get('email')
    code = data.get('otp_code')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Find the latest active OTP for this user
    otp_record = OTP.query.filter_by(
        user_id=user.user_id, 
        otp_code=code, 
        is_used=False,
        action="verification"
    ).order_by(OTP.created_at.desc()).first()

    if not otp_record or otp_record.expires_at < datetime.utcnow():
        return jsonify({"message": "Invalid or expired OTP"}), 400

    # Mark as verified
    user.is_verified = True
    otp_record.is_used = True
    db.session.commit()

    return jsonify({"message": "Account verified successfully. You can now login."}), 200