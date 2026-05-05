import os
from xhtml2pdf import pisa
from flask import render_template, current_app
from extensions import db
from datetime import datetime

# Import models
from Models.sales_model import Orders, OrderItem
from Models.post_sales_model import Invoice 
from Models.user_models import User, Address
from Models.product_models import Product

def generate_invoice_pdf(order_id):
    """
    Generates a PDF invoice for a given order and saves it to the database.
    """
    # 1. Fetch the Order
    order = Orders.query.get(order_id)
    if not order:
        return None

    # Check if invoice already exists to avoid duplicates
    existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
    if existing_invoice:
        return existing_invoice

    # 2. Fetch User and Address Details
    user = User.query.get(order.user_id)
    address = Address.query.get(order.address_id)

    # 3. Fetch Order Items and map them with Product Names
    order_items = OrderItem.query.filter_by(order_id=order.orders_id).all()
    items_data = []
    
    for oi in order_items:
        product = Product.query.get(oi.product_id)
        items_data.append({
            'item_id': oi.product_id,
            'name': product.name if product else 'Unknown Product',
            'quantity': oi.quantity,
            'unit_price': oi.price_at_purchase,
            'total_price': oi.quantity * oi.price_at_purchase
        })

    # 4. Generate Professional Invoice Number
    date_str = datetime.now().strftime("%Y%m%d")
    invoice_number = f"INV-{date_str}-{order.orders_id}"

    # 5. Setup Paths for Local Storage
    invoices_dir = os.path.join(current_app.root_path, 'static', 'invoices')
    os.makedirs(invoices_dir, exist_ok=True) 
    
    pdf_filename = f"{invoice_number}.pdf"
    pdf_filepath = os.path.join(invoices_dir, pdf_filename)
    pdf_url = f"/static/invoices/{pdf_filename}"

    # 6. Render HTML Template with ALL the new data
    html_content = render_template(
        'invoice_template.html', 
        order=order, 
        user=user,
        address=address,
        items=items_data,
        invoice_number=invoice_number,
        date=datetime.now().strftime("%d %B, %Y")
    )

    # 7. Convert HTML to PDF and Save
    with open(pdf_filepath, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        
    if pisa_status.err:
        raise Exception("Failed to generate PDF invoice")

    # 8. Save Invoice Record to Database
    new_invoice = Invoice(
        order_id=order.orders_id,
        invoice_number=invoice_number,
        pdf_url=pdf_url
    )
    db.session.add(new_invoice)
    db.session.commit()

    return new_invoice