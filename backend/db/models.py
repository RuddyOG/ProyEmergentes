from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Numeric
from sqlalchemy.sql import func
from db.postgres import Base

class Aire(Base):
    __tablename__ = "aire"
    
    id = Column(Integer, primary_key=True, index=True)
    devaddr = Column(String(20))
    dev_eui = Column(String(20))
    tenant_name = Column(String(50))
    device_name = Column(String(50))
    device_profile_name = Column(String(50))
    description = Column(Text)
    address = Column(Text)
    co2 = Column(Integer)
    temperature = Column(Numeric(5, 2))
    humidity = Column(Numeric(5, 2))
    battery = Column(Integer)
    status = Column(String(20))
    time = Column(DateTime)
    location_lat = Column(Numeric(10, 6))
    location_lng = Column(Numeric(10, 6))

class Sonido(Base):
    __tablename__ = "sonido"
    
    id = Column(Integer, primary_key=True, index=True)
    devaddr = Column(String(20))
    dev_eui = Column(String(20))
    tenant_name = Column(String(50))
    device_name = Column(String(50))
    device_profile_name = Column(String(50))
    description = Column(Text)
    address = Column(Text)
    laeq = Column(Numeric(6, 2))
    lai = Column(Numeric(6, 2))
    lai_max = Column(Numeric(6, 2))
    battery = Column(Integer)
    status = Column(String(20))
    time = Column(DateTime)
    location_lat = Column(Numeric(10, 6))
    location_lng = Column(Numeric(10, 6))
    frequency = Column(Integer)
    dr = Column(Integer)
    adr = Column(Boolean)

class Soterrado(Base):
    __tablename__ = "soterrado"
    
    id = Column(Integer, primary_key=True, index=True)
    devaddr = Column(String(20))
    dev_eui = Column(String(20))
    tenant_name = Column(String(50))
    device_name = Column(String(50))
    device_profile_name = Column(String(50))
    description = Column(Text)
    address = Column(Text)
    distance = Column(Numeric(5, 2))
    position = Column(String(20))
    battery = Column(Integer)
    status = Column(String(20))
    time = Column(DateTime)
    location_lat = Column(Numeric(10, 6))
    location_lng = Column(Numeric(10, 6))