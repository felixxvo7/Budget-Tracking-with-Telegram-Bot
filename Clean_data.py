from sqlalchemy import create_engine
import pandas as pd

# Create engine and load data
# Input: None
# Output: Loads income and expense data from the SQLite databases into Pandas DataFrames
engine = create_engine('sqlite:///income.db', echo=True)
df_income = pd.read_sql('income', con=engine)  # Load income data from 'income' table

engine = create_engine('sqlite:///expenses.db', echo=True)
df_expense = pd.read_sql('expenses', con=engine)  # Load expense data from 'expenses' table

# Remove duplicates which happen to be collected twice on the same date and same information
# Input: None
# Output: Removes duplicates from income and expense data where the same record appears twice
def remove_duplicates():
    # Drop duplicate rows based on specific columns for income and expenses
    df_income.drop_duplicates(subset=["date", "source", "amount", "note"], inplace=True)
    df_expense.drop_duplicates(subset=["date", "category", "reason", "amount", "note"], inplace=True)

# Remove duplicates which happen to have missing values
# Input: None
# Output: Removes rows with missing values in specific columns for income and expenses
def drop_na():
    # Drop rows where any of the specified columns have missing (NaN) values
    df_income.dropna(subset=["date", "source", "amount"], inplace=True)
    df_expense.dropna(subset=["date", "category", "reason", "amount"], inplace=True)

# Validate Data
# Input: None
# Output: Validates data by checking types and ensuring certain conditions hold for income and expense data
def validate_data():
    # Ensure 'amount' is of type float for both income and expense
    df_expense["amount"] = df_expense["amount"].astype(float)
    df_income["amount"] = df_income["amount"].astype(float)

    # Ensure 'amount' is positive by converting negative values to their absolute value
    df_expense["amount"] = df_expense["amount"].apply(lambda x: abs(x))
    df_income["amount"] = df_income["amount"].apply(lambda x: abs(x))

    # Ensure expense categories are valid
    expected_categories = ["G", "B", "F", "W", "M"]
    assert df_expense["category"].isin(expected_categories).all(), "Unexpected categories found in expenses"

# Return cleaned data in CSV
# Input: None
# Output: Cleans the data (removes duplicates, missing values, validates data), then saves cleaned data to CSV files
def return_clean_csv():
    # Call the data cleaning functions
    validate_data()  # Validate data types and category values
    drop_na()  # Remove rows with missing values
    remove_duplicates()  # Remove duplicate records

    # Save the cleaned data as CSV files
    df_income.to_csv('cleaned_income.csv', index=False)
    df_expense.to_csv('cleaned_expenses.csv', index=False)

# Call the function to clean and save the data
return_clean_csv()
