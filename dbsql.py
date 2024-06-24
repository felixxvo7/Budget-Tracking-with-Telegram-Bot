from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
import pandas as pd
Base = declarative_base()


class Expense(Base):
    __tablename__= "expenses"
    id_tracker = 0
    id = Column(Integer, primary_key=True,autoincrement=True)
    date = Column ("date", Date,nullable=False)
    category = Column("category", CHAR,nullable=False)
    reason = Column("reason", String, nullable= False )
    amount = Column("amount",Float, nullable=False)
    note = Column("note", String, nullable= True )

    def __init__(self, category, reason, amount, note = None):
        self.category = category
        self.reason = reason
        self.amount = amount
        self.date = date.today()
        if note == "No additional note":
            self.note = None
        else:
            self.note = note


    def __repr__(self) -> str:
        category_dict = {
            "G" : "Groceries",
            "B" : "Bill and Housing",
            "F" : "Fun (Shopping and Eating out)",
            "W" : "Wellness (Education and Health)",
            "M" : "Miscellaneous"
        }
        return (f"Expense:\n"
                f"Date: {self.date}\n"
                f"Category: {category_dict[self.category]}\n"
                f"Spending Reason: {self.reason}\n"
                f"Amount: {self.amount}\n"
                f"Note: {self.note}")
    
engine = create_engine('sqlite:///expenses.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_expense(category,reason,amount,note):
    new_expense = Expense(category=category,reason=reason,amount=amount,note=note)
    session.add(new_expense)
    session.commit()
    return new_expense

a = add_expense("G", "Food", 41.5,"Lunch")
b= add_expense("B", "Transport", 150,"No additional note" )
a1 = add_expense("G", "Food", 141.5,"Food for meeeeee <3")
b1= add_expense("B", "Rent", 550,"homing note" )
print(a)
print(b)
