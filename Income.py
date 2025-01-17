from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

# Create a base class for declarative class definitions
Base = declarative_base()

# Define the file name for exported income data
income_file = "exported_income.csv"

class Income(Base):
    """
    Represents an income entry in the database.

    Attributes:
        id (int): Unique identifier for the income entry.
        date (Date): Date the income was earned.
        source (str): Source of the income.
        amount (float): Amount of the income.
        note (str): Optional note associated with the income entry.
    """

    __tablename__ = "income"  # Define the database table name
    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    date = Column("date", Date, nullable=False)  # Date column, cannot be null
    source = Column("source", String, nullable=False)  # Source column, cannot be null
    amount = Column("amount", Float, nullable=False)  # Amount column, cannot be null
    note = Column("note", String, nullable=True)  # Note column, optional

    def __init__(self, source, amount, note=None):
        """Initializes an Income object."""
        self.source = source
        self.amount = amount
        self.date = date.today()  # Automatically set the date to today
        self.note = None if note == "No additional note" else note  # Set note or default

    def __repr__(self) -> str:
        """Returns a string representation of the Income object."""
        return (
            f"Income:\n"
            f"Date: {self.date}\n"
            f"Earned from: {self.source}\n"
            f"Amount: {self.amount}\n"
            f"Note: {self.note}."
        )

# Create an SQLite database engine
engine = create_engine('sqlite:///income.db', echo=True)

# Create all tables in the engine
Base.metadata.create_all(bind=engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a Session instance
session = Session()

def earn_command(message):
    """
    Processes an earn command from a user.

    Args:
        message (obj): User message object containing income details.

    Returns:
        new_income (obj): New income object added to the database.
    """
    # Extract user data from the message
    user_data = message.text[3:].split(', ')

    # Check if the correct number of fields is provided
    if len(user_data) not in [2, 3]:
        raise ValueError("Invalid number of fields!")

    # Assign fields to variables
    source, amount = user_data[:2]
    note = user_data[2] if len(user_data) == 3 else "No additional note"

    # Validate the amount field (must be a valid number)
    if not amount.replace('.', '', 1).isdigit():
        raise ValueError("Invalid amount!")

    # Convert amount to a float
    amount = float(amount)

    # Create a new income entry
    new_income = add_income(
        source=source,
        amount=amount,
        note=note
    )

    return new_income

def add_income(source, amount, note):
    """
    Adds a new income entry to the database.

    Args:
        source (str): Source of the income.
        amount (float): Amount of the income.
        note (str): Optional note associated with the income entry.

    Returns:
        new_income (obj): The newly added Income object.
    """
    new_income = Income(source=source, amount=amount, note=note)
    session.add(new_income)  # Add the new income entry to the session
    session.commit()  # Commit the transaction to the database
    return new_income

def income_summarize_monthly(year=None, month=None):
    """
    Summarizes monthly income for a specific year and month.

    Args:
        year (int, optional): The year to summarize. Defaults to the current year.
        month (int, optional): The month to summarize. Defaults to the current month.

    Returns:
        summary_str (str): A summary of the income for the specified month.
        total_amount (float): The total income amount for the specified month.
    """
    if year is None or month is None:
        today = datetime.today()
        year = today.year
        month = today.month

    # Query the database for income entries in the specified year and month
    summary = session.query(
        func.strftime("%Y-%m", Income.date).label('month'),
        func.sum(Income.amount).label('total_amount')
    ).filter(
        func.strftime("%Y", Income.date) == str(year),  # Filter by year
        func.strftime("%m", Income.date) == f"{month:02}"  # Filter by month (zero-padded)
    ).group_by('month').all()

    # Generate the summary string
    summary_str = "Monthly Income Summary:\n"
    for month, total_amount in summary:
        summary_str += f"Month: {month}, Total: ${total_amount:.2f}\n"

    return summary_str, total_amount

def get_last_earning():
    """
    Retrieves the last 5 income entries.

    Returns:
        list: A list of the 5 most recent Income objects.
    """
    last_earning = session.query(Income).order_by(Income.id.desc()).limit(5).all()
    return last_earning

def income_delete_by_id(id):
    """
    Deletes an income entry by its ID.

    Args:
        id (int): The ID of the income entry to delete.

    Returns:
        str: Success or error message.
    """
    delete = session.query(Income).filter(Income.id == id).first()
    if delete:
        session.delete(delete)
        session.commit()
        return f"Income with ID {id} deleted successfully."
    else:
        return f"No income found with ID {id}."

def get_last_income():
    """
    Retrieves the last 5 income entries with detailed information.

    Returns:
        list: A list of dictionaries representing the 5 most recent Income entries.
    """
    last_earnings = session.query(Income).order_by(Income.id.desc()).limit(5).all()
    result = []
    for earning in last_earnings:
        result.append({
            f"Earning ID: {earning.id}\n"
            f"Date: {earning.date}\n"
            f"Earned from: {earning.source}\n"
            f"Amount: {earning.amount}\n"
            f"Note: {earning.note}."
        })
    return result
