from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
import pandas as pd
Base = declarative_base()
expense_file = "exported_expenses.csv"

class Expense(Base):
    __tablename__= "expenses"
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
        self.note = None if note == "No additional note" else note


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

# Function to extract SQL table to CSV file
def export_expenses_to_csv():
    df = pd.read_sql('expenses', con=engine)
    df.to_csv(expense_file, index=False)

def expense_summarize_monthly():
   summary = session.query(
      func.strftime("%Y-%m",Expense.date).label('month'),
      Expense.category,
      func.sum(Expense.amount).label('total_amount')
   ).group_by('month',Expense.category).all()
   category_dict = {
        "G": "Groceries",
        "B": "Bill and Housing",
        "F": "Fun (Shopping and Eating out)",
        "W": "Wellness (Education and Health)",
        "M": "Miscellaneous"
    }
   summary_str = "Monthly Expense Summary by Category:\n"

   for month, category, total_amount in summary:
       summary_str += f"Month: {month}, Category: {category_dict[category]}, Total: ${total_amount:.2f}\n"
       
   return summary_str

export_expenses_to_csv()

