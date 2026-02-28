# services/auth.py

from core.db import SessionLocal
from models.schema import User

def login_user(username: str, password: str):
    db = SessionLocal()
    
    user = db.query(User).filter(
        User.username == username,
        User.is_active == True
    ).first()
    
    if user and user.password == password:
        return user
    
    return None
