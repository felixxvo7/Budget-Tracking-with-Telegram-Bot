from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

# Create a base class for declarative class definitions
Base = declarative_base()

# Define the file name for exported income data
income_file = "exported_income.csv"

class Income(Base):
    """Represents an income entry in the database."""

    __tablename__ = "income"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column("date", Date, nullable=False)
    source = Column("source", String, nullable=False)
    amount = Column("amount", Float, nullable=False)
    note = Column("note", String, nullable=True)

    def __init__(self, source, amount, note=None):
        """Initializes an Income object."""
        self.source = source
        self.amount = amount
        self.date = date.today()
        self.note = None if note == "No additional note" else note

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

# Create a configured "Session" class .
Session = sessionmaker(bind=engine)

# Create a Session
session = Session()

def earn_command(message):
    """Processes an earn command from a user."""
    # Get user data from the message
    user_data = message.text[3:].split(', ')

    # Check if the user provided 2 or 3 values
    if len(user_data) not in [2, 3]:
        raise ValueError("Invalid number of fields!")

    # Split the user data into source, amount, and optional note
    source, amount = user_data[:2]
    note = user_data[2] if len(user_data) == 3 else "No additional note"

    # Validate the amount field
    if not amount.replace('.', '', 1).isdigit():
        raise ValueError("Invalid amount!")

    # Cast amount to float
    amount = float(amount)

    # Create new income entry
    new_income = add_income(
        source=source,
        amount=amount,
        note=note
    )

    return new_income

def add_income(source, amount, note):
    """Adds a new income entry to the database."""
    new_income = Income(source=source, amount=amount, note=note)
    session.add(new_income)
    session.commit()
    return new_income


def income_summarize_monthly(year=None, month=None):
    """Summarizes monthly income."""
    if year is None or month is None:
        today = datetime.today()
        year = today.year
        month = today.month
        
    summary = session.query(
        func.strftime("%Y-%m", Income.date).label('month'),
        func.sum(Income.amount).label('total_amount')
    ).filter(
        func.strftime("%Y", Income.date) == str(year),  # Filter by year
        func.strftime("%m", Income.date) == f"{month:02}"  # Filter by month (zero-padded)
    ).group_by('month').all()

    summary_str = "Monthly Income Summary:\n"
    for month, total_amount in summary:
        summary_str += f"Month: {month}, Total: ${total_amount:.2f}\n"

    return summary_str

def get_last_earning():
    """Retrieves the last 5 income entries."""
    last_earning = session.query(Income).order_by(Income.id.desc()).limit(5).all()
    return last_earning

def income_delete_by_id(id):
    """Deletes an income entry by its ID."""
    delete = session.query(Income).filter(Income.id == id).first()
    if delete:
        session.delete(delete)
        session.commit()
        return f"Income with ID {id} deleted successfully."
    else:
        return f"No income found with ID {id}."

def get_last_income():
    """Retrieves the last 5 income entries with detailed information."""
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
