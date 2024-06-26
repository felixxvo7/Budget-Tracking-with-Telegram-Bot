from Expense import Expense
from Income import Income
import telebot
from telebot import types
import os

def save_expense_to_file(expense : Expense,ex_file_path):
    with open(ex_file_path,'a') as f:
        f.write(f"{expense.date},{expense.category},{expense.reason},{expense.amount},{expense.note}\n")

def save_income_to_file(income : Income,in_file_path):
    with open(in_file_path,'a') as f:
        f.write(f"{income.date},{income.reason},{income.amount},{income.note}\n")

def summarize(type , file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
     
    if type == "expense":
        expenses = []
        with open(file_path,"r") as exf:
            lines = exf.readlines()
            for line in lines:
                expense_data_line = line.strip()
                try:
                    expense_date, expense_category, expense_reason, expense_amount, expense_note = expense_data_line.split(",")
                    expense_data = Expense(
                        date=expense_date,
                        category=expense_category,
                        reason=expense_reason,
                        amount=float(expense_amount),
                        note=expense_note
                    )

                    expenses.append(expense_data)
                except ValueError as e:
                    print(f"Skipping line due to error: {e}")
        return expenses
    elif type == "income":
        income = []
        with open(file_path,"r") as inf:
            lines = inf.readlines()
            for line in lines:
                income_data_line = line.strip()
                try:
                    income_date, income_reason, income_amount, income_note = income_data_line.split(",")
                    income_data = Income(
                        date=income_date,
                        reason=income_reason,
                        amount=float(income_amount),
                        note=income_note
                    )
                    income.append(income_data)
                except ValueError as e:
                    print(f"Skipping line due to error: {e}")

        return income
    else:        
        raise ValueError("Invalid type. Expected 'expense' or 'income'.")
    
def summarize_total(type , file_path):
    data_list = []
    amounts =0

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    data_list = summarize(type , file_path)
    if type == "expense":
        amounts = sum(Expense.amount for Expense in data_list)
    elif type == "income":
        amounts = sum(Income.amount for Income in data_list)
    else:        
        raise ValueError("Invalid type. Expected 'expense' or 'income'.")
    return amounts

#Function to sum by category
def summarize_by_category(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
     
    expense_list = summarize("expense" , file_path)
    amount_by_category ={}
    for expense in expense_list:
        key = expense.category
        if key in amount_by_category:
            amount_by_category[key] += expense.amount
        else:
            amount_by_category[key] = expense.amount
    return amount_by_category
