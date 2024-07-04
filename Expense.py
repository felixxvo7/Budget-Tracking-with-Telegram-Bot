from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from Budget import Budget, get_budget
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
    
    def get_category(self):
        return self.category
    
    def get_amount(self):
        return self.amount

    
engine = create_engine('sqlite:///expenses.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

category_dict = {
        "G": "Groceries",
        "B": "Bill and Housing",
        "F": "Fun (Shopping and Eating out)",
        "W": "Wellness (Education and Health)",
        "M": "Miscellaneous"
    }
def spend_command(message):
        # split user data by commas
        user_data = message.text[3:].split(', ') 

        # check if 3 or 4 fields are provided
        if  len(user_data) not in [3, 4]:
            raise ValueError("Invalid number of fields!")

        # assign fields to variables
        category, reason, amount = user_data[:3]
        note = user_data[3] if len(user_data) == 4 else "No additional note" 
        
        # Handling error for Category field:
        if category not in ['G', 'B', 'F', 'W', 'M']:
            raise ValueError("""Invalid category. Category must be in: 
                G - Groceries
                B - Bill and Housing
                F - Fun (Shopping and Eating out)
                W - Wellness (Education and Health)
                M - Miscellaneous """) 

        # Handling error for Amount field:
        if not amount.replace('.','',1).isdigit():
            raise ValueError("Invalid amount!")

        
        #cast amount 
        amount = float(amount)

        # create new expense:
        new_expense = add_expense(
                        category=category,
                        reason= reason,
                        amount= amount,
                        note = note)
        return new_expense
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
   """
    Generates a monthly expense summary by category.

    This function queries the database to retrieve the total amount spent in each category
    for each month, and returns a string summarizing the results.

    Parameters:
    None

    Returns:
    str: A string summarizing the monthly expense by category.

    Example:
    >>> expense_summarize_monthly()
    Monthly Expense Summary by Category:
    Month: 2022-01, Category: Groceries, Total: $500.00
    Month: 2022-01, Category: Bill and Housing, Total: $1500.00
    Month: 2022-02, Category: Fun (Shopping and Eating out), Total: $200.00
   ...
    """
   summary = session.query(
      func.strftime("%Y-%m",Expense.date).label('month'),
      Expense.category,
      func.sum(Expense.amount).label('total_amount')
   ).group_by('month',Expense.category).all()
   
   summary_str = "Monthly Expense Summary by Category:\n"

   for month, category, total_amount in summary:
       summary_str += f"Month: {month}, Category: {category_dict[category]}, Total: ${total_amount:.2f}\n"
       
   return summary_str

def get_last_expense():
    last_expenses =  session.query(Expense).order_by(Expense.id.desc()).limit(5).all()
    result= []
    for expense in last_expenses:
        result.append({
                f"Expense ID: {expense.id}\n"
                f"Date: {expense.date}\n"
                f"Category: {category_dict[expense.category]}\n"
                f"Spending Reason: {expense.reason}\n"
                f"Amount: {expense.amount}\n"
                f"Note: {expense.note}"})
    return result

def expense_delete_by_id(id):
    delete = session.query(Expense).filter(Expense.id == id).first()
    if delete:
        session.delete(delete)
        session.commit()
        return f"Expense with ID {id} deleted sucessfully."
    else:
        return f"No expense found with ID {id}."

def get_budget_message(category, amount):

    budget_dict, budget_total = get_budget()

    if category in budget_dict:
        budget_value = budget_dict[category]


    sort_by_category = session.query(
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m"),
        Expense.category == category
    ).all()

    recorded_by_category = sort_by_category[0][0] if sort_by_category[0][0] is not None else 0

    total_budget = session.query(
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m"),
    ).all()

    recorded_total = total_budget[0][0] if total_budget[0][0] is not None else 0

    recorded_by_category = round(recorded_by_category, 2)
    category_diff = budget_value - (recorded_by_category + amount)
    total_diff = budget_total - (recorded_total + amount)


    return_str = f" Category Budget Remaining {category_diff}\nTotal Budget Remaining {total_diff}"

    return return_str

export_expenses_to_csv()
