from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv('DB_URL','sqlite:///./database.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, index=True, unique=True)
    ts = Column(DateTime, index=True, default=datetime.utcnow)
    sender = Column(String, index=True)
    recipients = Column(Text)
    subject = Column(Text)
    size = Column(Integer, default=0)
    has_attachment = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    meta = Column(Text, default='')

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, index=True, default=datetime.utcnow)
    email_uid = Column(String, index=True)
    severity = Column(String, default='medium')
    message = Column(Text)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()
    print('DB initialized')
