# services/user_service.py

from sqlalchemy.orm import Session
from models.schema import User
from services.auth import hash_password


# =========================================================
# OBTENER TODOS LOS USUARIOS
# =========================================================
def get_all_users(db: Session):
    return db.query(User).order_by(User.id).all()


# =========================================================
# OBTENER USUARIO POR ID
# =========================================================
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# =========================================================
# OBTENER USUARIO POR USERNAME
# =========================================================
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# =========================================================
# CREAR USUARIO (PASSWORD HASH)
# =========================================================
def create_user(db: Session, username: str, password: str, role: str):

    # Verificar si ya existe
    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise Exception("El usuario ya existe")

    hashed_password = hash_password(password)

    new_user = User(
        username=username,
        password=hashed_password,
        role=role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================================================
# ACTUALIZAR USUARIO
# =========================================================
def update_user(db: Session, user_id: int, update_data: dict):

    user = get_user_by_id(db, user_id)

    if not user:
        raise Exception("Usuario no encontrado")

    for key, value in update_data.items():

        # 🔐 Manejo especial de password
        if key == "password":

            # Si viene vacío, NO actualizar
            if not value:
                continue

            # Si ya parece un hash bcrypt, no re-hashear
            if value.startswith("$2b$") or value.startswith("$2a$"):
                continue

            # Si es password nueva válida
            value = hash_password(value)

        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user



# =========================================================
# ELIMINAR USUARIO
# =========================================================
def delete_user(db: Session, user_id: int):

    user = get_user_by_id(db, user_id)

    if not user:
        raise Exception("Usuario no encontrado")

    db.delete(user)
    db.commit()

    return True
