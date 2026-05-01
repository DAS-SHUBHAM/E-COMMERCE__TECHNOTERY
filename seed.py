from app import create_app
from extensions import db, bcrypt
from Models.user_models import User, Role
import uuid

app = create_app()

def seed_database():
    with app.app_context():
        # 1. Create tables
        db.create_all()

        # 2. Create Roles with audit fields
        if not Role.query.filter_by(role_id=1).first():
            print("Creating Roles...")
            # We provide 1 for created_by/updated_by to satisfy MySQL constraints
            admin_role = Role(role_id=1, role_name='admin', created_by=1, updated_by=1)
            seller_role = Role(role_id=2, role_name='seller', created_by=1, updated_by=1)
            user_role = Role(role_id=3, role_name='user', created_by=1, updated_by=1)
            
            db.session.add_all([admin_role, seller_role, user_role])
            # Use flush to test constraints before final commit
            db.session.flush() 

        # 3. Create Admin User
        if not User.query.filter_by(email="admin@system.com").first():
            print("Creating Admin User...")
            admin_user = User(
                uuid=str(uuid.uuid4()),
                username="super_admin",
                email="admin@system.com",
                password=bcrypt.generate_password_hash("admin123").decode('utf-8'),
                role_id=1,
                is_verified=True,
                is_active=True,
                created_by=1, # Provide the audit IDs
                updated_by=1
            )
            db.session.add(admin_user)
            
        db.session.commit()
        print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_database()