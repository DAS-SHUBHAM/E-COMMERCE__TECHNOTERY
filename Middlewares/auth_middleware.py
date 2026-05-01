from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from Models.user_models import User

def role_required(role_id):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user.role_id != role_id:
                return jsonify({"msg": "Permission denied"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper