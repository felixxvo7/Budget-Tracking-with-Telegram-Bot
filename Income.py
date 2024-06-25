from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
import pandas as pd

Base = declarative_base()


class Income(Base):
    __tablename__= "income"
    id = Column(Integer, primary_key=True,autoincrement=True)
    date = Column ("date", Date,nullable=False)
    source = Column("source", String, nullable= False )
    amount = Column("amount",Float, nullable=False)
    note = Column("note", String, nullable= True )

    def __init__(self, source, amount, note = None):
        self.source = source
        self.amount = amount
        self.date = date.today()
        if note == "No additional note":
            self.note = None
        else:
            self.note = note


    def __repr__(self) -> str:
        return ("Income:\n"
                f"Date: {self.date}\n"
                f"Earned from: {self.source}\n"
                f"Amount: {self.amount}\n"
                f"Note: {self.note}.")
    
engine = create_engine('sqlite:///income.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_income(source,amount,note):
    new_income= Income(source=source,amount=amount,note=note)
    session.add(new_income)
    session.commit()
    return new_income

