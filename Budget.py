from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLAlchemy Base
Base = declarative_base()

# Represents a budget entry in the database
"""
Attributes:
    id (int): Unique identifier for the budget entry.
    category (str): Category of the budget entry (e.g. "G" for Groceries).
    amount (float): Amount allocated to the budget category.
"""
class Budget(Base):
    __tablename__ = 'budget'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    # Initializes a new Budget instance.
    def __init__(self, category, amount):
        self.category = category
        self.amount = amount

# Initialize the database
engine = create_engine('sqlite:///budget.db')
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
# Create a Session
session = Session()

# Manages a budget by parsing user input, storing data in a database, and providing summary information.
class BudgetManager:
    category_list = ['G', 'B', 'F', 'W', 'M']

    def __init__(self):
        self.bud_list = []  # Stores the budget amounts for each category
        self.bud_category = []  # Stores the categories for the budget
        self.total_budget = 0  # Total budget amount across all categories
        self.bud_dict = {}  # Dictionary mapping categories to their budget amounts

    # Parses a user-provided message to extract budget information.
    # Input: A message string containing budget data (e.g., "/setbud G 100, B 200, F 50, W 75, M 40")
    # Output: Parses and stores the budget data; throws errors if message is invalid
    def parse_message(self, message):
        if not message or len(message) < 8:
            raise ValueError("Invalid message!")

        user_data = message[8:].split(', ')  # Extract budget data from the message

        if len(user_data) != 5:
            raise ValueError("Invalid number of fields!")

        # Extract category and amount from the user's message
        for i in user_data:
            i = i.strip()
            budget = i.split(' ')
            if budget:
                if not budget[1].replace('.', '', 1).isdigit():
                    raise ValueError("Invalid amount!")
                self.bud_list.append(float(budget[1]))  # Add the amount to the list
                self.total_budget += float(budget[1])  # Add the amount to the total budget
                self.bud_category.append(budget[0])  # Add the category to the list
            else:
                raise ValueError("Syntax error! Please try again.")

        # Check if the correct number of categories was provided
        if len(self.bud_category) != len(self.category_list):
            raise ValueError("Incorrect number of categories! Please try again.")

        # Ensure that the correct order of categories was provided
        for i in range(len(self.category_list)):
            if self.bud_category[i] != self.category_list[i]:
                raise ValueError("Categories are incorrect! Please try again.")
            
        self.bud_dict = dict(zip(self.bud_category, self.bud_list))  # Create a dictionary of categories and amounts

        # Save to the database
        self.save_to_db()

    # Returns a summary of the budget in a message string format.
    # Input: None
    # Output: A string summarizing the budget by category
    def get_budget_summary(self):
        return (f"Groceries: {self.bud_list[0]}\n"
                f"Bill and Housing: {self.bud_list[1]}\n"
                f"Fun: {self.bud_list[2]}\n"
                f"Wellness: {self.bud_list[3]}\n"
                f"Miscellaneous: {self.bud_list[4]}")

    # Returns total budget
    # Input: None
    # Output: Total budget amount across all categories
    def get_total_budget(self):
        return self.total_budget
    
    # Returns dictionary of the budget object carries
    # Input: None
    # Output: A dictionary mapping categories to their budget amounts
    def get_budget_dict(self):
        return self.bud_dict
    
    # Store data in the database
    # Input: None
    # Output: Saves the budget data to the database and clears existing data
    def save_to_db(self):
        # Clear existing data from the 'budget' table
        session.query(Budget).delete()

        # Add the new budget data to the database
        for category, amount in self.bud_dict.items():
            budget_entry = Budget(category=category, amount=amount)
            session.add(budget_entry)

        session.commit()

# Returns amount of budget in setup of category dict and total budget amount
# Input: None
# Output: A tuple containing a dictionary of categories and amounts, and the total budget amount
def get_budget():
    budget_category = {}
    budgets = session.query(Budget).all()  # Retrieve all budget entries from the database
    total_amount = 0  # Initialize total budget amount
    for budget in budgets:
        budget_category[budget.category] = budget.amount  # Map categories to their amounts
        total_amount += budget.amount  # Add the amount to the total budget

    return budget_category, total_amount

# Returns a formatted string of the current budget summary
# Input: None
# Output: A string summarizing the budget in a user-friendly format
def print_budget():
    # Get the budget details from the database
    budget_category, total_amount = get_budget()
    
    # Format the budget for display
    summary_str = "Current Budget Summary:\n"
    for category, amount in budget_category.items():
        # Convert the category to a more readable format
        category_name = {
            'G': 'Groceries',
            'B': 'Bill and Housing',
            'F': 'Fun (Shopping and Eating out)',
            'W': 'Wellness (Education and Health)',
            'M': 'Miscellaneous'
        }.get(category, 'Unknown Category')  # Default to 'Unknown Category' if the category is not found
        
        # Add the category and amount to the summary string
        summary_str += f"{category_name}: ${amount:.2f}\n"

    # Add the total budget at the end
    summary_str += f"Total Budget: ${total_amount:.2f}"

    return summary_str
