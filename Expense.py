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
    
    __tablename__ = "expenses"
    
    # Define columns for the expenses table
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column("date", Date, nullable=False)
    category = Column("category", CHAR, nullable=False)
    reason = Column("reason", String, nullable=False)
    amount = Column("amount", Float, nullable=False)
    note = Column("note", String, nullable=True)

    def __init__(self, category, reason, amount, note=None):
        """
        Initializes an Expense object with provided details.
        
        Args:
            category (str): The category of the expense.
            reason (str): The reason for the expense.
            amount (float): The amount of the expense.
            note (str, optional): Any additional notes for the expense.
        """
        self.category = category
        self.reason = reason
        self.amount = amount
        self.date = date.today()
        self.note = None if note == "No additional note" else note

    def __repr__(self) -> str:
        """
        Provides a string representation of the Expense object.
        
        Returns:
            str: Formatted string representing the Expense object.
        """
        category_dict = {
            "G": "Groceries",
            "B": "Bill and Housing",
            "F": "Fun (Shopping and Eating out)",
            "W": "Wellness (Education and Health)",
            "M": "Miscellaneous"
        }
        return (f"Expense:\n"
                f"Date: {self.date}\n"
                f"Category: {category_dict[self.category]}\n"
                f"Spending Reason: {self.reason}\n"
                f"Amount: {self.amount}\n"
                f"Note: {self.note}")

    def get_category(self):
        """
        Returns the category of the expense.
        
        Returns:
            str: Category of the expense.
        """
        return self.category

    def get_amount(self):
        """
        Returns the amount of the expense.
        
        Returns:
            float: Amount of the expense.
        """
        return self.amount


# Database connection and setup
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
    Processes a spend command from a user to create and add an expense to the database.
    
    Args:
        message (obj): User message object containing spend details.
    
    Returns:
        new_expense (obj): New Expense object added to the database.
    """
    # split user data by commas
    user_data = message.text[3:].split(', ') 

    # check if 3 or 4 fields are provided
    if len(user_data) not in [3, 4]:
        raise ValueError("Invalid number of fields!")

    # assign fields to variables
    category, reason, amount = user_data[:3]
    note = user_data[3] if len(user_data) == 4 else "No additional note" 

    # Handling error for Category field
    if category not in ['G', 'B', 'F', 'W', 'M']:
        raise ValueError("""Invalid category. Category must be in: 
            G - Groceries
            B - Bill and Housing
            F - Fun (Shopping and Eating out)
            W - Wellness (Education and Health)
            M - Miscellaneous """) 

    # Handling error for Amount field
    if not amount.replace('.','',1).isdigit():
        raise ValueError("Invalid amount!")

    # Cast amount to float
    amount = float(amount)

    # Create new expense and add it to the database
    new_expense = add_expense(
                    category=category,
                    reason=reason,
                    amount=amount,
                    note=note)
    return new_expense

def add_expense(category, reason, amount, note):
    """
    Adds a new expense to the database.
    
    Args:
        category (str): Category of the expense.
        reason (str): Reason for the expense.
        amount (float): Amount of the expense.
        note (str): Optional note for the expense.
    
    Returns:
        new_expense (obj): The newly added Expense object.
    """
    new_expense = Expense(category=category, reason=reason, amount=amount, note=note)
    session.add(new_expense)
    session.commit()
    return new_expense

def expense_summarize_monthly(year=None, month=None):
    """
    Summarizes monthly expenses by category.
    
    Args:
        year (int, optional): Year for the summary. Defaults to current year if not provided.
        month (int, optional): Month for the summary. Defaults to current month if not provided.
    
    Returns:
        str: Monthly expense summary as a string.
    """
    if year is None or month is None:
        today = datetime.today()
        year = today.year
        month = today.month

    # Query expenses for the specified month and year
    summary = session.query(
        func.strftime("%Y-%m", Expense.date).label('month'),
        Expense.category,
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y", Expense.date) == str(year),  # Filter by year
        func.strftime("%m", Expense.date) == f"{month:02}"  # Filter by month (zero-padded)
    ).group_by('month', Expense.category).all()

    # Prepare the summary string
    summary_str = "Monthly Expense Summary by Category:\n"
    for month, category, total_amount in summary:
        summary_str += f"Month: {month}, Category: {category_dict[category]}, Total: ${total_amount:.2f}\n"

    return summary_str

def get_last_expense():
    """
    Retrieves the last 5 expenses from the database.
    
    Returns:
        list: A list of strings representing the last 5 expenses.
    """
    last_expenses = session.query(Expense).order_by(Expense.id.desc()).limit(5).all()
    result = []
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
    """
    Deletes an expense entry from the database by its ID.
    
    Args:
        id (int): ID of the expense to be deleted.
    
    Returns:
        str: Confirmation message of successful or unsuccessful deletion.
    """
    delete = session.query(Expense).filter(Expense.id == id).first()
    if delete:
        session.delete(delete)
        session.commit()
        return f"Expense with ID {id} deleted successfully."
    else:
        return f"No expense found with ID {id}."
