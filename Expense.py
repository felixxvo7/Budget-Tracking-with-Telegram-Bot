from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from Budget import Budget, get_budget
Base = declarative_base()
expense_file = "exported_expenses.csv"

class Expense(Base):
    """
    Represents an expense entry in the database.

    Attributes:
        id (int): Unique identifier for the expense.
        date (Date): Date of the expense.
        category (char): Category of the expense (G, B, F, W, M).
        reason (str): Reason for the expense.
        amount (float): Amount of the expense.
        note (str): Optional note for the expense.

    Methods:
        __init__: Initializes an Expense object.
        __repr__: Returns a string representation of the Expense object.
        get_category: Returns the category of the expense.
        get_amount: Returns the amount of the expense.
    """
    
    __tablename__= "expenses"
    id = Column(Integer, primary_key=True,autoincrement=True)
    date = Column ("date", Date,nullable=False)
    category = Column("category", CHAR,nullable=False)
    reason = Column("reason", String, nullable= False )
    amount = Column("amount",Float, nullable=False)
    note = Column("note", String, nullable= True )

    #Initializes an Expense object.
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
    
    #Returns the category of the expense
    def get_category(self):
        return self.category
    
    #Returns the amount of the expense
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
        """
        Processes a spend command from a user.
    
        Args:
            message (obj): User message object containing spend details.
    
        Returns:
            new_expense (obj): New expense object added to the database.
        """    
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

#Adds a new expense to the database.
def add_expense(category,reason,amount,note):
    new_expense = Expense(category=category,reason=reason,amount=amount,note=note)
    session.add(new_expense)
    session.commit()
    return new_expense

def expense_summarize_monthly(year = None , month = None):
   """Summarizes monthly expenses by category."""

   if year is None or month is None:
        today = datetime.today()
        year = today.year
        month = today.month

     # Query expenses for the specified month and year
   summary = session.query(
      func.strftime("%Y-%m",Expense.date).label('month'),
      Expense.category,
      func.sum(Expense.amount).label('total_amount')
   ).filter(
        func.strftime("%Y", Expense.date) == str(year),  # Filter by year
        func.strftime("%m", Expense.date) == f"{month:02}"  # Filter by month (zero-padded)
    ).group_by('month',Expense.category).all()
   
   summary_str = "Monthly Expense Summary by Category:\n"

   for month, category, total_amount in summary:
       summary_str += f"Month: {month}, Category: {category_dict[category]}, Total: ${total_amount:.2f}\n"
       
   return summary_str

def get_last_expense():
    #Retrieves the last 5 expenses.
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
    #Deletes an expense by ID.
    delete = session.query(Expense).filter(Expense.id == id).first()
    if delete:
        session.delete(delete)
        session.commit()
        return f"Expense with ID {id} deleted sucessfully."
    else:
        return f"No expense found with ID {id}."

