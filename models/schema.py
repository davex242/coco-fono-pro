# models/schema.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Float, Numeric, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, date
from core.db import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    mico_id = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False)  # "admin" o "user"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
class Emitter(Base):
    __tablename__ = "emitters"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    mico_id = Column(String, unique=True, index=True)
    metodo_pago = Column(String)
    pago_id = Column(String)
    fecha_registro = Column(Date)
    telefono = Column(String)
    reclutador_nombre = Column(String)
    reclutador_id = Column(String, ForeignKey("users.mico_id"))
    estado_cuenta = Column(String, default="Pendiente")  # pendiente, verificada, rechazada, cancelada
    fecha_verificacion = Column(Date)
    estado_comision = Column(String, default="Pendiente")  # pendiente, pagada
    monto_comision = Column(Integer, default=25)
    check_real = Column(Boolean, default=False)
    captura_form = Column(String, nullable=True)
    captura_pago = Column(String, nullable=True)
    captura_transmision = Column(String, nullable=True)
    captura_chat = Column(String, nullable=True)

    reclutador = relationship("User")
    
class CommissionRule(Base):
    __tablename__ = "commission_rules"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, default="Configuración Global")

    monto_base = Column(Float, default=10)
    bonus_real = Column(Float, default=15)
    multiplicador = Column(Float, default=1)
    meta_minima = Column(Integer, default=10000)

    activa = Column(Boolean, default=True)

    # 🔥 AQUÍ ESTÁ LO NUEVO
    configuracion = Column(JSON, default=dict)

class CommissionRecord(Base):
    __tablename__ = "commission_records"

    id = Column(Integer, primary_key=True)
    emitter_id = Column(Integer, ForeignKey("emitters.id"))
    reclutador_id = Column(Integer, ForeignKey("users.id"))
    monto = Column(Float)
    fecha_generacion = Column(DateTime, default=datetime.now)
    pagada = Column(Boolean, default=False)
    pagado = Column(Boolean, default=False)
    fecha_pago = Column(DateTime, nullable=True)

class CommissionHistory(Base):
    __tablename__ = "commission_history"

    id = Column(Integer, primary_key=True, index=True)

    recruiter_id = Column(String, index=True)

    total_cuentas = Column(Integer, default=0)
    cuentas_reales = Column(Integer, default=0)

    monto_base = Column(Float)
    bonus_real = Column(Float)
    multiplicador = Column(Float)

    total_pagado = Column(Float)

    fecha = Column(DateTime, default=datetime.now)

    pagado = Column(Boolean, default=False)
    fecha_pago = Column(DateTime, nullable=True)