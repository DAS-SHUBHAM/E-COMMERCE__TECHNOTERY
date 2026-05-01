from flask import jsonify

def register_error_handlers(app):
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "status": "error",
            "code": 400,
            "message": "Bad Request: The server could not understand the request."
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            "status": "error",
            "code": 401,
            "message": "Unauthorized: Invalid or missing authentication token."
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "status": "error",
            "code": 403,
            "message": "Forbidden: You do not have permission to perform this action."
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "status": "error",
            "code": 404,
            "message": "Resource not found: The requested URL or ID does not exist."
        }), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        # Log the actual error here for debugging (e.g., app.logger.error(e))
        return jsonify({
            "status": "error",
            "code": 500,
            "message": "Internal Server Error: Something went wrong on our end."
        }), 500

    # Custom Error for Database Integrity (e.g., Duplicate Emails)
    from sqlalchemy.exc import IntegrityError
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        return jsonify({
            "status": "error",
            "code": 409,
            "message": "Database Conflict: This record (likely email or username) already exists."
        }), 409