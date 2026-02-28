# services/emitter.py
import streamlit as st
from sqlalchemy.orm import Session
from models.schema import Emitter, User
from datetime import datetime
from core.db import SessionLocal
import os
import shutil

UPLOAD_FOLDER = r"c:\Users\deivi\oneDrive\Escritorio\coco_fono_pro\assets\uploads"

import os
import shutil
from models.schema import Emitter
import stat

def handle_remove_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)
    
def remove_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_emitters_by_ids(db, ids):

    emitters = (
        db.query(Emitter)
        .filter(Emitter.id.in_(ids))
        .all()
    )

    for emitter in emitters:

        mico_folder = str(emitter.mico_id).strip()
        folder_path = os.path.join(UPLOAD_FOLDER, mico_folder)

        st.write("Intentando borrar carpeta:", folder_path)

        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path, onexc=handle_remove_readonly)
                st.write("Carpeta eliminada correctamente")
            except Exception as e:
                st.write("Error eliminando carpeta:", e)
        else:
            st.write("Carpeta NO encontrada:", folder_path)

    # Eliminar registros en DB
    (
        db.query(Emitter)
        .filter(Emitter.id.in_(ids))
        .delete(synchronize_session=False)
    )

    db.commit()
        
def delete_emitters_by_mico_ids(db, mico_ids):
    if not mico_ids:
        return []

    emitters = (
        db.query(Emitter)
        .filter(Emitter.mico_id.in_(mico_ids))
        .all()
    )

    if not emitters:
        return []

    # services

    deleted_micos = []

    try:

        for emitter in emitters:

            mico_id = str(emitter.mico_id).strip()
            folder_path = os.path.join(UPLOAD_FOLDER, mico_id)

            st.write("Intentando borrar:", folder_path)
            
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path, onexc=handle_remove_readonly)
                    st.write("Carpeta eliminada correctamente")
                except Exception as e:
                    st.write("Error eliminando carpeta:", e)
            else:
                st.write("Carpeta NO encontrada:", folder_path)



            db.delete(emitter)
            deleted_micos.append(mico_id)

        db.flush()     # 🔥 fuerza ejecución
        db.commit()

        st.write("Commit realizado correctamente")

    except Exception as e:
        db.rollback()
        st.write("ERROR GENERAL:", e)

    return deleted_micos

def get_emitter_by_mico_id(db, mico_id):
    return db.query(Emitter).filter(Emitter.mico_id == mico_id).first()

def get_all_emitters(db: Session):
    """
    Retorna todos los emisores (emitters) de la base de datos.
    """
    return db.query(Emitter).all()

def get_emitters_by_recruiter(db: Session, recruiter_id):
    """
    Retorna todos los emisores asignados a un reclutador específico.
    """
    return db.query(Emitter).filter(Emitter.reclutador_id == recruiter_id).all()


def create_emitter(db:Session, data):
    """
    Crea un nuevo emisor y lo guarda en la base de datos.
    """
    existing = get_emitter_by_mico_id(db, data["mico_id"])
    if existing:
        raise ValueError("Ya existe un emisor con ese Mico ID")

    else:
        nuevo_emitter = Emitter(
            nombre=data["nombre"],
            mico_id=data["mico_id"],
            metodo_pago=data["metodo_pago"],
            pago_id=data["pago_id"],
            fecha_registro=data["fecha_registro"],      
            telefono=data["telefono"],
            reclutador_nombre=data["reclutador_nombre"],
            reclutador_id=data["reclutador_id"],
            estado_cuenta=data["estado_cuenta"],
            fecha_verificacion=data["fecha_verificacion"],
            estado_comision=data["estado_comision"],
            check_real=data["check_real"],
            captura_form=data["captura_form"],
            captura_pago=data["captura_pago"],
            captura_transmision=data["captura_transmision"],
            captura_chat=data["captura_chat"],
        )
        db.add(nuevo_emitter)
        db.commit()
        db.refresh(nuevo_emitter)
        return nuevo_emitter


def get_emitter_by_id(db: Session, emitter_id: int):
    """
    Retorna un emisor por su ID.
    """
    return db.query(Emitter).filter(Emitter.id == emitter_id).first()

#-------------------------------------------------------------------------
def get_emitters_by_mico_ids(db, mico_ids):

    if not mico_ids:
        return []

    return (
        db.query(Emitter)
        .filter(Emitter.mico_id.in_(mico_ids))
        .all()
    )