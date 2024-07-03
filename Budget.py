from sqlalchemy import create_engine, Column, String, Integer, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    limit = Column(Float, nullable=False)
    month = Column(Date, nullable=False)

    def __init__(self, category, limit, month):
        self.category = category
        self.limit = limit
        self.month = month

    def __repr__(self) -> str:
        return f"Budget(Category: {self.category}, Limit: {self.limit}, Month: {self.month})"

engine = create_engine('sqlite:///budget.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

def set_budget(category, limit, month):
    budget = Budget(category=category, limit=limit, month=month)
    session.add(budget)
    session.commit()
    return budget

def get_budget(category, month):
    budget = session.query(Budget).filter_by(category=category, month=month).first()
    return budget

def update_budget(category, limit, month):
    budget = session.query(Budget).filter_by(category=category, month=month).first()
    if budget:
        budget.limit = limit
        session.commit()
    return budget
