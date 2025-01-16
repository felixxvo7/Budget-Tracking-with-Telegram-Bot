from Expense import Expense
from Income import Income
import os

def save_expense_to_file(expense : Expense,ex_file_path):
    with open(ex_file_path,'a') as f:
        f.write(f"{expense.date},{expense.category},{expense.reason},{expense.amount},{expense.note}\n")

def save_income_to_file(income : Income,in_file_path):
    with open(in_file_path,'a') as f:
        f.write(f"{income.date},{income.reason},{income.amount},{income.note}\n")
