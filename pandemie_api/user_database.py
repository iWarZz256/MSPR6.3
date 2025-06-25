from models import User
from database import SessionLocal
from passlib.hash import bcrypt

db = SessionLocal()

admin = User(
    username="admin",
    password_hash=bcrypt.hash("adminpassword"),
    is_admin=True
)

user = User(
    username="user",
    password_hash=bcrypt.hash("userpassword"),
    is_admin=False
)

db.add(admin)
db.add(user)
db.commit()
db.close()
