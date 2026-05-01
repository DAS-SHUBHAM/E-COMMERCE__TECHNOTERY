import uuid
import random
import string
from datetime import datetime, timedelta
from flask import render_template
from flask_mail import Message
from extensions import mail, db
import smtplib

def generate_uuid():
    """Generates a unique string for public IDs."""
    return str(uuid.uuid4())

def generate_otp(length=6):
    """Generates a numeric OTP for verification."""
    return ''.join(random.choices(string.digits, k=length))

def format_currency(amount):
    """Ensures currency is returned with 2 decimal places."""
    return "{:.2f}".format(amount if amount else 0)

def calculate_order_total(items_with_prices):
    """
    Calculates total amount for order placement.
    Expects a list of dictionaries with 'price' and 'quantity'.
    """
    return sum(item['price'] * item['quantity'] for item in items_with_prices)

def get_current_timestamp():
    """Returns standard UTC timestamp."""
    return datetime.utcnow()

# --- NEW: Email Helper ---

def send_otp_email(receiver_email, otp_code, template_name='otp_mail.html'):
    """
    Sends a styled HTML email with the OTP code.
    Requires 'templates/otp_mail.html' to exist.
    """
    try:
        msg = Message(
            subject="Action Required: Verify Your Account",
            sender="sd745461@gmail.com",
            recipients=[receiver_email]
        )
        # This renders the HTML file from your /templates folder
        msg.html = render_template(template_name, otp_code=otp_code)
        mail.send(msg)
        return True
    except Exception as e:
        # In development, this helps you see why the email failed
        print(f"CRITICAL: Email failed to send to {receiver_email}. Error: {str(e)}")
        return False

# --- NEW: Useful Additions for E-commerce ---

def is_otp_expired(expiry_time):
    """Checks if the OTP has passed its expiration window."""
    return datetime.utcnow() > expiry_time

def calculate_discount(price, discount_percentage):
    """Calculates final price after discount."""
    if not discount_percentage:
        return price
    discount_amount = (price * discount_percentage) / 100
    return price - discount_amount