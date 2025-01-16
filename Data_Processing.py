import os
from Expense import Expense
from Income import Income
from Budget import Budget, get_budget
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from Budget import Budget, get_budget
import numpy as np

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
#
# Category-Specific Analysis
#
def get_budget_message(category):
    """Generates a message about the remaining budget for a category and total budget, and returns data in an array."""
    
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
    
    # Add the array for the budget data
    array_data = np.array([[
        budget_value, 
        recorded_by_category, 
        category_diff, 
        budget_total, 
        recorded_total, 
        total_diff
    ]])
    
    return return_str, array_data

def check_budget():
    """Checks the remaining budget by category and total, and returns data in an array."""
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

    # Initialize the summary string and a list to hold category data
    summary_str = "Monthly Expense Summary by Category:\n"
    category_data = []

    # Iterate through the summary results and calculate the remaining budget for each category
    for category, total_amount in totals_by_category.items():
        recorded_amount = totals_by_category.get(category, 0)
        remaining_budget_category = budget_dict.get(category, 0) - recorded_amount
        summary_str += f"Category: {category_dict.get(category, 'Unknown')}, Remaining Total: ${remaining_budget_category:.2f}\n"
        
        # Append the category data to the list
        category_data.append([category, budget_dict.get(category, 0), recorded_amount, remaining_budget_category])

    # Calculate the total remaining budget
    total_remaining = budget_total - recorded_total
    summary_str += f"\nTotal Budget Remaining: ${total_remaining:.2f}"

    # Convert the category data list to a NumPy array
    category_data_array = np.array(category_data, dtype=object)
    
    return summary_str, category_data_array

#
# Overall Spending vs. Budget
#
def overall_spending_vs_budget():
    """Compares overall spending with the allocated budget and handles overspending."""
    # Retrieve the budget dictionary and total budget from the get_budget function
    budget_dict, budget_total = get_budget()

    # Query the database to get the total amount spent in the current month
    total_budget_spent = session.query(
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m")
    ).all()

    # Retrieve the total amount spent, default to 0 if None
    total_spent = total_budget_spent[0][0] if total_budget_spent[0][0] is not None else 0

    # Calculate the overall budget vs spending percentage
    if budget_total > 0:
        overall_percentage_spent = (total_spent / budget_total) * 100
    else:
        overall_percentage_spent = 0

    # Check for overspending
    if total_spent > budget_total:
        overspent_amount = total_spent - budget_total
        overspent_str = f"OVERSPENT! You have overspent by: ${overspent_amount:.2f}\n"
    else:
        overspent_str = "You are within the budget.\n"

    # Create the message string for overall spending
    overall_comparison_str = f"Overall Budget: ${budget_total:.2f}\n"
    overall_comparison_str += f"Total Spent: ${total_spent:.2f}\n"
    overall_comparison_str += f"Percentage of Budget Spent: {overall_percentage_spent:.2f}%\n"
    overall_comparison_str += overspent_str

    # Return both the message and the array of data
    overall_data = np.array([[budget_total, total_spent, overall_percentage_spent, overspent_amount if total_spent > budget_total else 0]])
    return overall_comparison_str, overall_data


def category_spending_vs_budget():
    """Compares spending by category with the allocated budget and handles overspending."""
    # Retrieve the budget dictionary and total budget from the get_budget function
    budget_dict, budget_total = get_budget()

    # Query the database to get the total amount spent in the current month by category
    category_spent = session.query(
        Expense.category,
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        func.strftime("%Y-%m", Expense.date) == datetime.now().strftime("%Y-%m")
    ).group_by(
        Expense.category
    ).all()

    # Initialize the message string and a list to store category data
    category_comparison_str = "Category Spending vs Budget:\n"
    category_data = []

    for category, total_spent in category_spent:
        # Retrieve the budget for the current category
        budget_for_category = budget_dict.get(category, 0)
        
        # Calculate the percentage spent for the current category
        if budget_for_category > 0:
            percentage_spent = (total_spent / budget_for_category) * 100
        else:
            percentage_spent = 0
        
        # Check if the category is overspent
        if total_spent > budget_for_category:
            overspent_amount = total_spent - budget_for_category
            overspent_str = f"OVERSPENT! You have overspent by: ${overspent_amount:.2f}\n"
        else:
            overspent_str = "You are within the budget for this category.\n"
        
        # Add category comparison information to the string
        category_comparison_str += f"Category: {category_dict.get(category, 'Unknown')}\n"
        category_comparison_str += f"Budgeted: ${budget_for_category:.2f}\n"
        category_comparison_str += f"Spent: ${total_spent:.2f}\n"
        category_comparison_str += f"Percentage of Budget Spent: {percentage_spent:.2f}%\n"
        category_comparison_str += overspent_str + "\n"

        # Store the data in a list for output
        category_data.append([category, budget_for_category, total_spent, percentage_spent, overspent_amount if total_spent > budget_for_category else 0])

    # Convert the list to a NumPy array for the category data
    category_data_array = np.array(category_data, dtype=object)
    return category_comparison_str, category_data_array
