from sqlalchemy import create_engine
import pandas as pd

#Create engine and load data
engine = create_engine('sqlite:///income.db', echo=True)
df_income = pd.read_sql('income',con=engine)

engine = create_engine('sqlite:///expenses.db', echo=True)
df_expense = pd.read_sql('expenses', con = engine)

#Remove duplicates which happens to be collected twice in the same date and same information
def remove_duplicates():
    df_income.drop_duplicates(subset=["date","source", "amount", "note"],inplace = True)
    df_expense.drop_duplicates(subset=["date","category", "reason", "amount","note"],inplace = True)
 
#Remove duplicates which happens to be missing values
def drop_na():
    df_income.dropna(subset=["date","source", "amount"],inplace = True)
    df_expense.dropna(subset=["date","category", "reason", "amount"],inplace = True)

#Validate Data
def validate_data():
    df_expense["amount"]= df_expense["amount"].astype(float)
    df_income["amount"]= df_income["amount"].astype(float)

    df_expense["amount"]= df_expense["amount"].apply(lambda x: abs(x))
    df_income["amount"]= df_income["amount"].apply(lambda x: abs(x))

    expected_categories = ["G", "B", "F", "W", "M"]
    assert df_expense ["category"].isin(expected_categories).all(),"Unexpected categories found in expenses "

#Return Cleaned Data in csv
def return_clean_csv():
    #call function
    validate_data()
    drop_na()
    remove_duplicates()

    df_income.to_csv('cleaned_income.csv', index=False)
    df_expense.to_csv('cleaned_expenses.csv', index=False)

return_clean_csv()