import telebot
from telebot import types
import os
from dotenv import load_dotenv
from Budget import Budget
from Expense import Expense, add_expense, expense_delete_by_id, expense_summarize_monthly, get_last_expense, spend_command
from Income import Income, add_income, earn_command, get_last_income, income_delete_by_id, income_summarize_monthly
from Methods import save_expense_to_file, save_income_to_file, summarize_by_category, summarize_total
from datetime import date
load_dotenv()
key = os.getenv('APIBUDGET')
bot_name = os.getenv('NAMEBUDGET')
BOT_TOKEN = key
BOT_USERNAME = bot_name
bot = telebot.TeleBot(BOT_TOKEN)

# Hello and welcome the user when start the conversation.
@bot.message_handler(commands=['start', 'hello','hi'])
def send_welcome(message):
    user_first_name = str(message.chat.first_name) 
    welcoming = f"""Hello {user_first_name}!
🚀 Welcome, my name is Aurelius 🤖 - Your Personal Financial Assistant!📊💰

With the power of data science algorithms, we're making financial management a breeze!🌟
Our goal is to provide you with instant insights into your transactions, making your personal finance journey easy to control. Whether you're just getting started with budgeting or consider yourself a financial expert, I have your back.

Are you ready to make changes to how you manage your money? Let us embark on this financial journey with much love and dedication!💙💸

For more information: /help 🤖"""

    bot.reply_to(message, welcoming )
    
# Provides information about the bot and its features.
@bot.message_handler(commands=['about'])
def help_option(message):
    help_text ="""
      🤖 Aurelius - Your Financial Companion!📊💼

1.	Data Collection and Management: Collect and categorize transactions in real time; store data in Google Sheets or SQL for maximum flexibility.

2.	Data Analyze: Use advanced statistical models and Python algorithms to perform a detailed analysis of spending patterns, revealing actionable insights and providing you with a report once the data has been analyzed.

3.	Precision Financial Planning: Establish a financial goal, create dynamic monthly budgets, and adjust in real-time for disciplined fiscal management by displaying the differences between your planned and real-time financial status.

4.	Visualize Your Progress: Experience financial insights at a glance with dynamic charts and graphs showcasing your total monthly summary.
"""
    bot.send_message(message.chat.id, help_text )
    bot.send_message(message.chat.id, """All of this is designed for you to unleash the power of data-driven financial empowerment . Once in you life, you can finaly say: 'Financial freedom, here I come!' 
    For more information: /help """ )

 #Provides a list of available commands for the user.
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, """Hello! I'm your personal bot. 
    You can use the following commands:
    /start - Starts the bot
    /about - Tells you more about the bot
    /spend - Collect the your spending data
    /earn  - Collect the your earning data
    /summarize - See expense summary by category
    /setbud- Set buget for each month
    /view - show last 5 data in either Expense data or Income data
    /report- Report the summary of transactions for this month until now
    """)

# Collecting data
#Prompts the user to provide spending information.
@bot.message_handler(commands=['spend'])
def prompt_spend(message):
    bot.send_message(message.chat.id, """Sure! Please use the /s command with the format:
    '/s category, spending reason, amount, note (optional)'.

    for Categories: 
        G - Groceries
        B - Bill and Housing
        F - Fun (Shopping and Eating out)
        W - Wellness (Education and Health)
        M - Miscellaneous""")

#Processes the user's spending data provided in the format '/s: categories, spending reason, amount'
# message handler for spend command
@bot.message_handler(func=lambda message: message.text.startswith('/s '))
def process_spend_command(message):
    try:
        new_expense = spend_command(message)
        
        #send formatted message to user
        bot.send_message(message.chat.id,new_expense)
        bot.send_message(message.chat.id,"For more information about summary of your expenses: /ExpenseSum ")
    except ValueError as e:
        # Error message in process_spend_command
        bot.send_message(message.chat.id, f"Error: {e}\n"
        "Please provide the information in the correct format:\n'/s category, spending reason, amount, note'")

# Collecting data
# Used to ask about the information for the purpose to collect earning data
@bot.message_handler(commands=['earn'])
def prompt_earn(message):
    bot.send_message(message.chat.id, """Sure! Please use the /e command with the format:
     '/e earned from, amount, note (optional)'.
    """)

# Handle the earn command
@bot.message_handler(func=lambda message: message.text.startswith('/e '))
def process_earn_command(message):
    try:
        new_income = earn_command(message)
        # Send a message to the user with the earned information
        bot.send_message(message.chat.id,new_income)
        bot.send_message(message.chat.id,"For more information about summary of your income: /IncomeSum")
        
    except ValueError as e:
        # Send an error message to the user if they provided the wrong number of values
        bot.send_message(message.chat.id,f"Error: {e} \n" "Please provide the information in the correct format: '/e earned from, amount, note'.")

@bot.message_handler(commands=['ExpenseSum'])
def expense_summary_command(message):
    bot.send_message(message.chat.id,expense_summarize_monthly())

@bot.message_handler(commands=['IncomeSum'])
def expense_summary_command(message):
    bot.send_message(message.chat.id,income_summarize_monthly())
        
@bot.message_handler(commands=['LastExpense'])
def expense_preview(message):
    last_expenses = get_last_expense()
    for expense in last_expenses:
        bot.send_message(message.chat.id,expense)

@bot.message_handler(commands=['LastIncome'])
def income_preview(message):
    last_earnings = get_last_income()
    for earning in last_earnings:
        bot.send_message(message.chat.id,earning)

@bot.message_handler(func=lambda message: message.text.startswith('/delete '))
def delete_expense(message):
    try:
        user_data = message.text.split(" ")

        if len(user_data) != 3:
            raise ValueError("Invalid number of fields!")
        
        data_type, data_id = user_data[1:3]
        result =""

        if data_type == "I": result = income_delete_by_id(data_id)

        elif data_type == "E": result = expense_delete_by_id(data_id)

        else: raise ValueError("Invalid type of fields! Data type is either E or I ")

        bot.send_message(message.chat.id,result)
    except ValueError as e:
        # Error message in process_spend_command
        bot.send_message(message.chat.id, f"Error: {e}\n"
        "Please provide the information in the correct format:\n'/delete (data type E or I) id'")

        
@bot.message_handler(func=lambda message: message.text.startswith('/setbud '))
def set_budget_command(message):
    try:
        budget = Budget(message)
        budget.parse_message()
        bot.send_message(message.chat.id, f"Budget is set with:\n{budget.get_budget_summary()}")
        bot.send_message(message.chat.id, f"Total budget set: {budget.get_total_budget()}")

    except ValueError as e:
        # Error message in process_spend_command
        bot.send_message(message.chat.id, f"Error: {e}\n"
        "Please provide the information in the correct format:\n'/setbud G int, B int, F int, W int, M int '")

bot.polling()

