# E-Commerce Custom Backend Infrastructure Engine
A production-ready, modular, and highly secure micro-backend built using Python and Flask. This architecture is engineered to handle complex vendor ecosystems, real-time communication modules, secure transaction flows, and isolated multi-asset bulk catalog operations with strict relational data integrity.

## 🚀 Key Technical Highlights & Architecture

*   **Dynamic Bulk Catalog Ingestion:** Parses multi-part `form-data` streams containing raw CSV manifests and complex `.zip` media archives synchronously without losing track of relational mapping context.
*   **Hierarchical Storage Isolation:** Prevents data race conditions and security leaks by routing physical static files into strictly isolated storage grids using unique Seller & Product UUID tokens rather than predictable incremental integer IDs:
    `static/uploads/products/seller_<seller_uuid>/product_<product_uuid>/<image_uuid>.<extension>`
*   **Flexible Schema Mappings:** Avoids static database fragmentation by mapping fluid inventory specifications (such as Size, Color, and Material) via a dynamic, normalized relational tracking layout.
*   **Granular Role-Based Access Control (RBAC):** Restricts administrative paths via verified JWT claims checks, ensuring only authenticated administrators can process merchant capability approvals.
*   **Comprehensive Error Guardrails:** Implements global exception wrappers alongside granular database session rollbacks (`db.session.rollback()`) to gracefully catch validation drops and database namespace conflicts.

---
## 🛠️ Technology Stack & Dependencies

*   **Core Framework:** Python 3.x, Flask
*   **Authentication Matrix:** Flask-JWT-Extended (Bearer Token Engine)
*   **Database & ORM Layer:** MySQL, SQLAlchemy, Flask-Migrate (Database Continuous Version Logs)
*   **Asynchronous & Extensions Layer:** Eventlet, Flask-SocketIO (Bidirectional Live Streams)
*   **File Utility Engine:** ZipFile processing, CSV DictReader parsing, Werkzeug security path sanitizers
---

## 📂 Structural Directory Overview

```text
📁 E-Commerce/                             # Root Project Workspace
│
├── 📁 Middlewares/                        # Custom Request Security & Filtering Layers
│   ├── 📄 auth_middleware.py              # User authentication verification setup
│   └── 📄 error_handler.py                # Global exception tracking & server error catchers
│
├── 📁 Models/                             # Core Relational Entity Blueprints
│   ├── 📄 __init__.py                     # Database framework schema bindings
│   ├── 📄 chat_model.py                   # Real-time message storage data structure
│   ├── 📄 post_sales_model.py             # Refund, tickets, and post-purchase architecture
│   ├── 📄 product_models.py               # Products, Inventory mappings & Specs grid
│   ├── 📄 sales_model.py                  # Revenue, core transactions & ordering analytics
│   └── 📄 user_models.py                  # Identity Management (Roles, IDs, Passwords)
│
├── 📁 Routes/                             # Business Logics & API Routing Engine
│   ├── 📁 Admin/                          # Protected Portal Management Tasks
│   │   ├── 📄 admin_order_updates.py      # Control system for overall marketplace deliveries
│   │   ├── 📄 approve_category.py         # Administrative vendor permissions gatekeeper
│   │   ├── 📄 create_category.py          # Platform catalogs blueprint instantiation
│   │   ├── 📄 delete_categories.py        # Obsolete marketplace asset purging system
│   │   ├── 📄 get_categories.py           # Universal hierarchy data fetchers
│   │   └── 📄 update_categories.py        # Catalog metadata modification controls
│   │
│   ├── 📁 Cart/                           # Customer Cart Sessions Management
│   │   ├── 📄 add_item.py                 # Basket expansion handling controller
│   │   ├── 📄 delete_from_cart.py         # Item retraction script layout
│   │   └── 📄 view_cart.py                # Active purchase pipeline aggregations
│   │
│   ├── 📁 Chat/                           # Live Support Channels Communication Core
│   │   ├── 📄 __init__.py                 # Socket routing instance allocations
│   │   └── 📄 chat_sockets.py             # WebSocket bidirectional channel streams
│   │
│   ├── 📁 Orders/                         # Checkout Engines & Transaction Records
│   │   ├── 📄 cancel_order.py             # Void transaction recovery controls
│   │   ├── 📄 get_history.py              # Customer archive ledger query handlers
│   │   ├── 📄 place_order.py              # Checkout initialization operational logic
│   │   └── 📄 track_order.py              # Transit logistics synchronization loops
│   │
│   ├── 📁 Products/                       # Public Catalog Browsing Capabilities
│   │   ├── 📄 List_all.py                 # Batch product query pipelines
│   │   ├── 📄 add_product.py              # Individual manual product creation route
│   │   ├── 📄 delete_product.py           # Catalog asset removal controller
│   │   ├── 📄 get_details.py              # Granular inventory metadata processing
│   │   └── 📄 update_product.py           # Existing product profile edits controller
│   │
│   ├── 📁 Seller/                         # Vendor Workspace Operations Cluster
│   │   ├── 📄 bulk_upload.py              # CSV/ZIP ingestion script mapped via secure UUID
│   │   ├── 📄 category_request.py         # Admin clearance requests initiator
│   │   └── 📄 get_my_requests.py          # Vendor authorization dashboard tracking
│   │
│   ├── 📁 User/                           # Consumer End Account Management
│   └── 📁 auth/                           # Authentication Endpoints Cluster
│   └── 📄 __init__.py                     # Main operational Blueprints compiler
│
├── 📁 Templates/                          # Operational Mail or HTML Layout Blueprints
├── 📁 migrations/                         # Flask-Migrate Continuous DB Version Control Logs
├── 📁 static/
│   └── 📁 invoices/                       # Automated checkout PDF tracking repositories
├── 📁 utils/                              # Shared Application Helper Tools & Framework Core Extensions
│
├── 📄 .gitignore                          # Tracking safe-lists blocking system caches & keys
├── 📄 app.py                              # Core Framework Initializer & Server Entrypoint
├── 📄 config.py                           # Application System Profiles & Connection Parameters
├── 📄 extensions.py                       # Interlocked global components initialization (db, jwt)
└── 📄 requirements.txt                    # Comprehensive Project Engine Dependencies Setup

🔧 Installation & Local Environment Setup

1. Clone the Workspace
Bash
git clone [https://github.com/DAS-SHUBHAM/E-Commerce__TECHNOTERY.git](https://github.com/DAS-SHUBHAM/E-Commerce__TECHNOTERY.git)
cd E-Commerce__TECHNOTERY

2. Instantiate and Activate the Virtual Environment

Bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate

3. Deploy Project Dependencies
Bash
pip install -r requirements.txt

4. Apply Database Version Upgrades
Ensure your local environment configuration details match your active MySQL database server schema credentials inside .env or config.py, then run:

Bash
flask db upgrade

5. Boot Up the Local Development Cluster
Bash
python app.py

🧪 API Operational Workflows (Key Postman Validation Milestones)

1. Administrative Clearance Pipeline
Endpoint: PUT /api/admin/approve-category/<request_uuid>

Headers:
Authorization: Bearer <ADMIN_JWT_TOKEN>
Content-Type: application/json
Request Body: {} (Enforces standard structured parsing context)
Database Resolution: Intercepts Admin claims, tracks the operational UUID request, updates is_approved and is_active fields, and permits the corresponding merchant to open bulk inventory batches.

2. Bulk Catalog Ingestion Process
Endpoint: POST /api/seller/products/bulk-upload
Headers:
Authorization: Bearer <SELLER_JWT_TOKEN>
Body (form-data):
csv_file: products.csv (Contains details for pricing, stock, categories, and custom specs)
zip_file: images.zip (Contains product image packs renamed precisely using SKU tokens, e.g., TSHIRT-OVR-101_1.jpg)

🔒 Security & Git Management Best Practices
To avoid exposing system junk files, authentication tokens, or compiled configurations to remote version tracks, ensure your root .gitignore parameters match the lines below:

Plaintext
# Local virtual environment
venv/
__pycache__/
instance/
.env

# Physical assets upload directory exclusions
static/uploads/bulk_temp/
static/uploads/products/
static/invoices/*.pdf

# Spreadsheet payloads and temporary archives
*.csv
*.zip
