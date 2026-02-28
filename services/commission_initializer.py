from sqlalchemy import inspect
from core.db import engine, SessionLocal, Base
from models.schema import CommissionRule


def initialize_commission_system():
    """
    1. Verifica si la tabla commission_rules existe
    2. Si no existe -> crea todas las tablas
    3. Si existe pero está vacía -> inserta configuración inicial
    """

    inspector = inspect(engine)

    # 🔎 Verificar si tabla existe
    if "commission_rules" not in inspector.get_table_names():
        print("Creando tabla commission_rules...")
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # 🔎 Verificar si hay alguna regla creada
    existing_rule = db.query(CommissionRule).first()

    if not existing_rule:
        print("Insertando configuración inicial de comisiones...")

        default_rule = CommissionRule(
            nombre="Configuración Global",
            monto_base=10.0,
            bonus_real=5.0,
            multiplicador=1.0,
            activa=True,
            configuracion={
                "descripcion": "Regla estándar inicial",
                "min_cuentas": 0,
                "requiere_reales": False
            }
        )

        db.add(default_rule)
        db.commit()

    db.close()
