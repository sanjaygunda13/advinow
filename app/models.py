from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime,func
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()


class Business(Base):
    __tablename__ = "business_details"

    business_id = Column(Integer, primary_key=True, unique=True,nullable=False)
    business_name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=True)
    phone = Column(Integer,nullable=True)
    address = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_date =  Column(String(100), nullable=True)

    
class Symptoms(Base):
    __tablename__ = "symptoms_details"
    symptom_id = Column(String, primary_key=True,unique=True,nullable=False )
    symptom_name = Column(String(120), nullable=True)
    init_treatment = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Diagnosis(Base):
    __tablename__ = "diagnosis_details" 
    diag_id = Column(Integer, primary_key=True,unique=True,autoincrement=True ) 
    business_id = Column(Integer, ForeignKey("business_details.business_id"))
    symptom_id = Column(String, ForeignKey("symptoms_details.symptom_id"))
    is_diagnosed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
