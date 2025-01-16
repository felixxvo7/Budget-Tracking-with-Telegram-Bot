import os
from Expense import Expense
from Income import Income
from Budget import Budget, get_budget
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from Budget import Budget, get_budget

Base = declarative_base()
engine = create_engine('sqlite:///expenses.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

category_dict = {
            "G" : "Groceries",
            "B" : "Bill and Housing",
            "F" : "Fun (Shopping and Eating out)",
            "W" : "Wellness (Education and Health)",
            "M" : "Miscellaneous"
        }

def get_budget_message(category):
    """Generates a message about the remaining budget for a category and total budget."""
    
    # Retrieve the budget dictionary and total budget from the get_budget function
    budget_dict, budget_total = get_budget()
    
    # Get the budget value for the specified category if it exists in the budget dictionary
    if category in budget_dict:
        budget_value = budget_dict[category]
    
    # Query the database to get the total amount spent in the current month for the specified category
    sort_by_category = session.query(
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m"),
        Expense.category == category
    ).all()
    
    # Retrieve the total amount spent for the specified category, default to 0 if None
    recorded_by_category = sort_by_category[0][0] if sort_by_category[0][0] is not None else 0
    
    # Query the database to get the total amount spent in the current month for all categories
    total_budget = session.query(
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m"),
    ).all()
    
    # Retrieve the total amount spent, default to 0 if None
    recorded_total = total_budget[0][0] if total_budget[0][0] is not None else 0
    

    # Calculate the remaining budget for the specified category and the total budget
    category_diff = budget_value - (recorded_by_category)
    total_diff = budget_total - (recorded_total)
    
    # Create the return message string with the remaining budget information
    return_str = f"Category Budget Remaining: {category_diff}\nTotal Budget Remaining: {total_diff}"
    
    return return_str



def check_budget():
    """Checks the remaining budget by category and total."""
    # Retrieve the budget dictionary and total budget from the get_budget function
    budget_dict, budget_total = get_budget()

    # Query the database to get the total amount spent in the current month grouped by category
    results = session.query(
        Expense.category,
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m")
    ).group_by(
        Expense.category
    ).all()

    # Create a dictionary of total amounts spent by category
    totals_by_category = {category: total_amount for category, total_amount in results}

    # Query the database to get the total amount spent in the current month
    total_budget = session.query(
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m")
    ).all()

    # Retrieve the total amount spent in the current month
    recorded_total = total_budget[0][0] if total_budget[0][0] is not None else 0

    # Query the database to get the monthly expense summary grouped by category
    summary = session.query(
        func.strftime("%Y-%m", Expense.date).label('month'),
        Expense.category,
        func.sum(Expense.amount).label('total_amount')
    ).group_by('month', Expense.category).all()

    # Initialize the summary string
    summary_str = "Monthly Expense Summary by Category:\n"

    # Iterate through the summary results and calculate the remaining budget for each category
    for month, category, total_amount in summary:
        recorded_amount = totals_by_category.get(category, 0)
        amount_by_category = budget_dict[category] - recorded_amount
        summary_str += f"Month: {month}, Category: {category_dict[category]},\nRemaining Total: ${amount_by_category:.2f}\n"

    # Calculate the total remaining budget
    total_remaining = budget_total - recorded_total
    summary_str += f"\nTotal Budget Remaining: ${total_remaining:.2f}"

    return summary_str


print()