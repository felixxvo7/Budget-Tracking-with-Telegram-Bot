from sqlalchemy import create_engine
import pandas as pd

#Create engine and load data
engine = create_engine('sqlite:///income.db')
df_income = pd.read_sql('income',con=engine)

engine = create_engine('sqlite///expenses.db')
df_expense = pd.read_sql('expense', con = engine)

#Remove duplicates
def remove_duplicates():
#Handle missing values
# Fill missing values or drop rows with missing values
def fillna():
def dropna():
#Handle inconsistent data/Convert Data Types
def format_handle():
#Filter Outliers
def IQR_filter():
#Validate Data
def validate_data():
#Return Cleaned Data in csv
df_income.to_csv('cleaned_income.csv', index=False)
df_expense.to_csv('cleaned_expenses.csv', index=False)