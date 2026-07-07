from flask import Flask
from extensions import db, jwt, bcrypt, migrate, mail, socketio
from config import Config
from flask_jwt_extended import jwt_required

# =======================================================
# 1. IMPORT GLOBAL ERROR HANDLERS
# =======================================================
from Middlewares.error_handler import register_error_handlers

# =======================================================
# 2. IMPORT API CONTROLLERS / FUNCTIONS 
# =======================================================
# Authentication Routes (Signup, Login, and OTP Verification)
from Routes.auth.Signup import signup_fn
from Routes.auth.Login import login_fn
from Routes.auth.Verify_otp import verify_otp_fn

# Cart Management Routes
from Routes.Cart.add_item import add_item_fn
from Routes.Cart.view_cart import view_cart_fn
from Routes.Cart.delete_from_cart import delete_item_fn  

# Product Operations Routes (Supports Role-based access control)
from Routes.Products.List_all import list_all_fn
from Routes.Products.get_details import get_details_fn
from Routes.Products.add_product import add_product_fn
from Routes.Products.update_product import update_product_fn
from Routes.Products.delete_product import delete_product_fn

# Order Processing and Tracking Routes
from Routes.Orders.place_order import place_order_fn
from Routes.Orders.get_history import get_history_fn
from Routes.Orders.track_order import track_order_fn
from Routes.Orders.cancel_order import cancel_order_item_fn

# Seller Specific Category Request & Bulk Catalog Operations Routes
from Routes.Seller.category_request import request_category_approval_fn
from Routes.Seller.get_my_requests import get_my_requests_fn
from Routes.Seller.bulk_upload import bulk_upload_products_fn

# Administrative Control Routes
from Routes.Admin.approve_category import approve_seller_category_fn
from Routes.Admin.create_category import create_category_fn
from Routes.Admin.get_categories import get_all_categories_fn
from Routes.Admin.update_categories import update_category_fn
from Routes.Admin.delete_categories import delete_category_fn
from Routes.Admin.admin_order_updates import update_order_status_admin_fn 

# User Specific Settings and Public Feeds Routes
from Routes.User.get_public_products import get_all_public_products_fn
from Routes.User.add_address import add_address_fn      
from Routes.User.get_address import get_addresses_fn  

# Core Payment Integrations (Razorpay), Wishlists, and Reviews Routes
from Routes.User.razorpay_payment import create_payment_order_fn, verify_payment_fn
from Routes.User.reviews import get_product_reviews_fn, add_review_fn
from Routes.User.wishlist import toggle_wishlist_fn, get_wishlist_fn


def create_app():
    """
    Application Factory function. Initializes extensions, configures settings,
    registers error handlers, and binds all API routing patterns.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------------------------------------------
    # INITIALIZE FLASK EXTENSIONS WTH APPLICATION CONTEXT
    # ---------------------------------------------------
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app) # Initializes WebSocket functionality
    
    # ---------------------------------------------------
    # REGISTER GLOBAL INTERCEPTORS / MIDDLEWARES
    # ---------------------------------------------------
    register_error_handlers(app)

    # ---------------------------------------------------
    # WEBSOCKET EVENT LISTENERS REGISTRATION
    # ---------------------------------------------------
    # Imported here to ensure socket event loops are active post extension initialization
    import Routes.Chat.chat_sockets

    # ---------------------------------------------------
    # HTTP API ROUTE REGISTRATION
    # ---------------------------------------------------
    
    # Public & Secured Authentication Endpoints
    app.add_url_rule('/api/auth/signup', view_func=signup_fn, methods=['POST'])
    app.add_url_rule('/api/auth/login', view_func=login_fn, methods=['POST'])
    app.add_url_rule('/api/auth/verify-otp', view_func=verify_otp_fn, methods=['POST'])

    # Core Product Catalog Endpoints (Public Browsing & Protected Seller Modifiers)
    app.add_url_rule('/api/products', view_func=list_all_fn, methods=['GET'])
    app.add_url_rule('/api/products/<product_uuid>', view_func=get_details_fn, methods=['GET'])
    app.add_url_rule('/api/products/add', view_func=add_product_fn, methods=['POST'])
    app.add_url_rule('/api/products/update/<product_uuid>', view_func=update_product_fn, methods=['PUT']) 
    app.add_url_rule('/api/products/delete/<product_uuid>', view_func=delete_product_fn, methods=['DELETE'])

    # Shopping Cart Utility Endpoints
    app.add_url_rule('/api/cart/add', view_func=add_item_fn, methods=['POST'])
    app.add_url_rule('/api/cart', view_func=view_cart_fn, methods=['GET'])
    app.add_url_rule('/api/cart/delete', view_func=delete_item_fn, methods=['DELETE'])  

    # Customer Checkout and Order Lifecycle Management Endpoints
    app.add_url_rule('/api/orders/place', view_func=place_order_fn, methods=['POST'])
    app.add_url_rule('/api/orders/history', view_func=get_history_fn, methods=['GET'])
    app.add_url_rule('/api/orders/track/<order_uuid>', view_func=track_order_fn, methods=['GET'])
    app.add_url_rule('/api/user/order/cancel/<string:order_item_uuid>', view_func=cancel_order_item_fn, methods=['PUT'])
    
    # Secure Administrative Operations Dashboard Endpoints
    app.add_url_rule('/api/admin/create-category', view_func=jwt_required()(create_category_fn), methods=['POST'])
    app.add_url_rule('/api/admin/approve-category/<request_uuid>', view_func=jwt_required()(approve_seller_category_fn), methods=['PUT'])
    app.add_url_rule('/api/admin/categories', view_func=jwt_required()(get_all_categories_fn), methods=['GET'])
    app.add_url_rule('/api/admin/update-category/<string:category_uuid>', view_func=jwt_required()(update_category_fn), methods=['PUT'])
    app.add_url_rule('/api/admin/delete-category/<string:category_uuid>', view_func=jwt_required()(delete_category_fn), methods=['DELETE'])
    app.add_url_rule('/api/admin/orders/update/<string:order_uuid>', view_func=update_order_status_admin_fn, methods=['PUT'])

    # Protected Merchant/Seller Store-Setup Endpoints
    app.add_url_rule('/api/seller/request-category', view_func=jwt_required()(request_category_approval_fn), methods=['POST'])
    app.add_url_rule('/api/seller/my-requests', view_func=get_my_requests_fn, methods=['GET'])
    
    # ADDED: Integrated Bulk Ingestion Endpoint for Sellers (Protected via JWT Context)
    app.add_url_rule('/api/seller/products/bulk-upload', view_func=bulk_upload_products_fn, methods=['POST'])

    # Consumer / Profile Specific Management Endpoints
    app.add_url_rule('/api/user/products-all', view_func=get_all_public_products_fn, methods=['GET'])
    app.add_url_rule('/api/user/add-address', view_func=add_address_fn, methods=['POST'])         
    app.add_url_rule('/api/user/addresses', view_func=get_addresses_fn, methods=['GET'])          
    app.add_url_rule('/api/payment/create/<string:order_uuid>', view_func=create_payment_order_fn, methods=['POST'])
    app.add_url_rule('/api/payment/verify', view_func=verify_payment_fn, methods=['POST'])
    
    # Engagement Endpoints (Wishlist State Toggles)
    app.route('/api/user/wishlist/toggle/<string:product_uuid>', methods=['POST'])(toggle_wishlist_fn)
    app.add_url_rule('/api/user/wishlist', view_func=jwt_required()(get_wishlist_fn), methods=['GET'])
    
    # Feedback and Social Proofing (Product Reviews) Endpoints
    app.route('/api/user/reviews/add/<string:product_uuid>', methods=['POST'])(add_review_fn)
    app.route('/api/public/reviews/<string:product_uuid>', methods=['GET'])(get_product_reviews_fn)
    
    return app


if __name__ == "__main__":
    app = create_app()
    # CRITICAL: Replaced standard app.run() with socketio.run() to host both 
    # traditional HTTP routes and real-time WebSocket protocol duplex loops simultaneously.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)