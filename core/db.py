# core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base 

import os

#DATABASE_URL = os.getenv("postgresql://postgres:Lunita200407%21%40%23@db.gsfzyqvymlsvnppvelnu.supabase.co:5432/postgres")#"sqlite:///coco_fono.db"

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres.gsfzyqvymlsvnppvelnu:Lunita200407%21%40%23@aws-1-us-east-2.pooler.supabase.com:5432/postgres" 
    #"postgresql://postgres:Lunita200407%21%40%23@db.gsfzyqvymlsvnppvelnu.supabase.co:5432/postgres"
    
    #"sqlite:///coco_fono.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()