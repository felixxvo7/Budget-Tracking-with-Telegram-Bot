from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
Base = declarative_base()


class Expense(Base):
    __tablename__= "expenses"
    id_tracker = 0
    id = Column(Integer, primary_key=True,autoincrement=True)
    date = Column ("date", DateTime)
    category = Column("category", CHAR)
    amount = Column(Float, nullable=False)
