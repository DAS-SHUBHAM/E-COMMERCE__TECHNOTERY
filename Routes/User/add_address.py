from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Models.user_models import Address
import uuid

@jwt_required()
def add_address_fn():
    user_id = get_jwt_identity()
    data = request.get_json()

    # =======================================================
    # 1. INPUT VALIDATION
    # =======================================================
    full_name    = data.get('full_name')
    phone_number = data.get('phone_number')
    street       = data.get('street')
    city         = data.get('city')
    state        = data.get('state')
    pincode      = data.get('pincode')
    is_default   = data.get('is_default', False)

    if not all([full_name, phone_number, street, city, state, pincode]):
        return jsonify({"message": "All fields are required: full_name, phone_number, street, city, state, pincode"}), 400

    # =======================================================
    # 2. IF THIS IS SET AS DEFAULT, UNSET ALL OTHER DEFAULTS
    # =======================================================
    try:
        if is_default:
            Address.query.filter_by(
                user_id=user_id,
                is_default=True
            ).update({"is_default": False})

        # =======================================================
        # 3. CREATE NEW ADDRESS
        # =======================================================
        new_address = Address(
            uuid=str(uuid.uuid4()),
            user_id=user_id,
            full_name=full_name,
            phone_number=phone_number,
            street=street,
            city=city,
            state=state,
            pincode=pincode,
            is_default=is_default,
            created_by=user_id,
            updated_by=user_id
        )
        db.session.add(new_address)
        db.session.commit()

        return jsonify({
            "message": "Address added successfully",
            "address_uuid": new_address.uuid
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to add address", "error": str(e)}), 500