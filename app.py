from flask import Flask
from extensions import db, jwt, bcrypt, migrate, mail
from config import Config
from flask_jwt_extended import jwt_required

# 1. Import Error Handlers 
from Middlewares.error_handler import register_error_handlers

# 2. Import API Functions   
# login/Signup/Verification routes
from Routes.auth.Signup import signup_fn
from Routes.auth.Login import login_fn
from Routes.auth.Verify_otp import verify_otp_fn

# Cart Routes-Add to cart, view cart and delete from cart
from Routes.Cart.add_item import add_item_fn
from Routes.Cart.view_cart import view_cart_fn
from Routes.Cart.delete_from_cart import delete_item_fn  

# Product Routes- View all products, get_details, add_products, update products(Authorization-seller)
from Routes.Products.List_all import list_all_fn
from Routes.Products.get_details import get_details_fn
from Routes.Products.add_product import add_product_fn
from Routes.Products.update_product import update_product_fn
from Routes.Products.delete_product import delete_product_fn

# Order Routes - Place_order, get_history and track_order(Authorization-User)
from Routes.Orders.place_order import place_order_fn
from Routes.Orders.get_history import get_history_fn
from Routes.Orders.track_order import track_order_fn
from Routes.Orders.cancel_order import cancel_order_item_fn

# Category Request Routes- category_request, get_my_requests (Authorization-Admin)
from Routes.Seller.category_request import request_category_approval_fn
from Routes.Seller.get_my_requests import get_my_requests_fn

# Admin Routes- approve_category, create_category, get_categories, update_categories, delete_categories, and update_order_status
from Routes.Admin.approve_category import approve_seller_category_fn
from Routes.Admin.create_category import create_category_fn
from Routes.Admin.get_categories import get_all_categories_fn
from Routes.Admin.update_categories import update_category_fn
from Routes.Admin.delete_categories import delete_category_fn
from Routes.Admin.admin_order_updates import update_order_status_admin_fn 

# Address Routes- add_address, get address and view all products without login(Authorization-User)
from Routes.User.get_public_products import get_all_public_products_fn
from Routes.User.add_address import add_address_fn      
from Routes.User.get_address import get_addresses_fn  

# Payment Route- create_payment_order, verify_payment_order (Authorization- User)
from Routes.User.razorpay_payment import create_payment_order_fn, verify_payment_fn

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions with the app
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Register Global Error Handlers
    register_error_handlers(app)

    # --- ROUTE REGISTRATION ---
    
    # Auth Routes
    app.add_url_rule('/api/auth/signup', view_func=signup_fn, methods=['POST'])
    app.add_url_rule('/api/auth/login', view_func=login_fn, methods=['POST'])
    app.add_url_rule('/api/auth/verify-otp', view_func=verify_otp_fn, methods=['POST'])

    # Product Routes (Public & Protected)
    app.add_url_rule('/api/products', view_func=list_all_fn, methods=['GET'])
    app.add_url_rule('/api/products/<product_uuid>', view_func=get_details_fn, methods=['GET'])
    app.add_url_rule('/api/products/add', view_func=add_product_fn, methods=['POST'])
    app.add_url_rule('/api/products/update/<product_uuid>', view_func=update_product_fn, methods=['PUT']) 
    app.add_url_rule('/api/products/delete/<product_uuid>', view_func=delete_product_fn, methods=['DELETE'])

    # Cart Routes
    app.add_url_rule('/api/cart/add', view_func=add_item_fn, methods=['POST'])
    app.add_url_rule('/api/cart', view_func=view_cart_fn, methods=['GET'])
    app.add_url_rule('/api/cart/delete', view_func=delete_item_fn, methods=['DELETE'])  

    # Order Routes
    app.add_url_rule('/api/orders/place', view_func=place_order_fn, methods=['POST'])
    app.add_url_rule('/api/orders/history', view_func=get_history_fn, methods=['GET'])
    app.add_url_rule('/api/orders/track/<order_uuid>', view_func=track_order_fn, methods=['GET'])
    app.add_url_rule('/api/user/order/cancel/<string:order_item_uuid>', view_func=cancel_order_item_fn, methods=['PUT'])
    
    # Admin Routes
    app.add_url_rule('/api/admin/create-category', view_func=jwt_required()(create_category_fn), methods=['POST'])
    app.add_url_rule('/api/admin/approve-category/<request_uuid>', view_func=jwt_required()(approve_seller_category_fn), methods=['PUT'])
    app.add_url_rule('/api/admin/categories', view_func=jwt_required()(get_all_categories_fn), methods=['GET'])
    app.add_url_rule('/api/admin/update-category/<string:category_uuid>', view_func=jwt_required()(update_category_fn), methods=['PUT'])
    app.add_url_rule('/api/admin/delete-category/<string:category_uuid>', view_func=jwt_required()(delete_category_fn), methods=['DELETE'])
    app.add_url_rule('/api/admin/orders/update/<string:order_uuid>', view_func=update_order_status_admin_fn, methods=['PUT'])

    # Seller Routes
    app.add_url_rule('/api/seller/request-category', view_func=jwt_required()(request_category_approval_fn), methods=['POST'])
    app.add_url_rule('/api/seller/my-requests', view_func=get_my_requests_fn, methods=['GET'])

    # User Routes
    app.add_url_rule('/api/user/products-all', view_func=get_all_public_products_fn, methods=['GET'])
    app.add_url_rule('/api/user/add-address', view_func=add_address_fn, methods=['POST'])        
    app.add_url_rule('/api/user/addresses', view_func=get_addresses_fn, methods=['GET'])         
    app.add_url_rule('/api/payment/create/<string:order_uuid>', view_func=create_payment_order_fn, methods=['POST'])
    app.add_url_rule('/api/payment/verify', view_func=verify_payment_fn, methods=['POST'])

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)