import psycopg2
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE = "scanner_db"
USERNAME = "scanner" 
PASSWORD = "password123"
HOST = "localhost"
PORT = "5432"

# Setup SQLAlchemy
engine = create_engine(f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')
Session = sessionmaker(bind=engine)

# Declare model base
Base = declarative_base()

# Result model
class Result(Base):
  __tablename__ = 'results'

  id = Column(Integer, primary_key=True)
  url = Column(String)
  issues = Column(String)

# Issue model  
class Issue(Base):
  __tablename__ = 'issues'

  id = Column(Integer, primary_key=True) 
  result_id = Column(Integer, ForeignKey('results.id'))
  type = Column(String)
  description = Column(String)

# Connect to db on import  
try:
  conn = engine.connect()
except psycopg2.OperationalError:
  print("Database connection failed")

# Utility functions
def init_db():
  Base.metadata.create_all(engine)

def get_session():
  session = Session()
  return session
