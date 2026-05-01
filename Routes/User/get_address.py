from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.user_models import Address

@jwt_required()
def get_addresses_fn():
    user_id = get_jwt_identity()

    addresses = Address.query.filter_by(
        user_id=user_id,
        is_active=True
    ).all()

    if not addresses:
        return jsonify({"message": "No addresses found", "addresses": []}), 200

    result = []
    for addr in addresses:
        result.append({
            "address_uuid": addr.uuid,
            "full_name":    addr.full_name,
            "phone_number": addr.phone_number,
            "street":       addr.street,
            "city":         addr.city,
            "state":        addr.state,
            "pincode":      addr.pincode,
            "is_default":   addr.is_default
        })

    return jsonify({"addresses": result}), 200