import telebot
from telebot import types
import os
from dotenv import load_dotenv
from Budget import Budget, BudgetManager
from Expense import Expense, check_budget, expense_delete_by_id, expense_summarize_monthly, get_budget_message, get_last_expense, spend_command
from Income import Income, earn_command, get_last_income, income_delete_by_id, income_summarize_monthly
from datetime import date
# Load environment variables from a .env file
load_dotenv()

# Retrieve the bot token and name from environment variables
key = os.getenv('APIBUDGET')
bot_name = os.getenv('NAMEBUDGET')
BOT_TOKEN = key
BOT_USERNAME = bot_name

# Initialize the bot with the token
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
    start_text = "Welcome to the financial bot! Use the following commands to manage your finances: \n" \
                 "/about - Tells you more about the bot \n" \
                 "/spend - Collect your spending data \n" \
                 "/earn  - Collect your earning data \n" \
                 "/summarize - See expense summary by category \n" \
                 "/budget- Set budget for each category \n" \
                 "/expense_sum - Summarize expenses by month \n" \
                 "/income_sum - Summarize income by month \n" \
                 "/last_expense - To view last 5 transactions of Expense \n" \
                 "/last_income - To view last 5 transactions of Income \n" \
                 "/view - show last 5 transactions in either Expense data or Income data \n" \
                 "/check_budget - show me the remaining budget for all category current month"\
                 "/report- Report the summary of transactions for this month until now"
    bot.reply_to(message, start_text)

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

# Processes the user's spending data provided in the format '/s: categories, spending reason, amount'
# message handler for spend command
@bot.message_handler(func=lambda message: message.text.startswith('/s '))
def process_spend_command(message):
    try:
        global budget_manager
        new_expense = spend_command(message)
        category = new_expense.get_category()
        amount = new_expense.get_amount()
        report = get_budget_message(category , amount)
        #send formatted message to user
        bot.send_message(message.chat.id,new_expense)
        bot.send_message(message.chat.id,report)
        bot.send_message(message.chat.id,"For more information about summary of your expenses: /expense_sum ")
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
        bot.send_message(message.chat.id,"For more information about summary of your income: /income_sum")
        
    except ValueError as e:
        # Send an error message to the user if they provided the wrong number of values
        bot.send_message(message.chat.id,f"Error: {e} \n" "Please provide the information in the correct format: '/e earned from, amount, note'.")

# Handler for the /ExpenseSum command
# Provides a sum of the recorded expenses
@bot.message_handler(commands=['expense_sum'])
def expense_summary_command(message):
    bot.send_message(message.chat.id,expense_summarize_monthly())


# Handler for the /IncomeSum command
# Provides a sum of the recorded earnings
@bot.message_handler(commands=['income_sum'])
def expense_summary_command(message):
    bot.send_message(message.chat.id,income_summarize_monthly())

# Handler for the /LastExpense command
# Provides a preview of the last recorded expenses
@bot.message_handler(commands=['last_expense'])
def expense_preview(message):
    last_expenses = get_last_expense()
    for expense in last_expenses:
        bot.send_message(message.chat.id, expense)

# Handler for the /LastIncome command
# Provides a preview of the last recorded incomes
@bot.message_handler(commands=['last_income'])
def income_preview(message):
    last_earnings = get_last_income()
    for earning in last_earnings:
        bot.send_message(message.chat.id, earning)

@bot.message_handler(commands=['view'])
def preview_command(message):
    str_out = """To view last 5 transactions of Expenses: /last_expense 
To view last 5 transactions of Income: /last_income                                                         """
    bot.send_message(message.chat.id, str_out)

# Handler for the /delete command
# Deletes an expense or income by ID
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

# Handler for the /setbud command
# Sets a new budget with detailed parameters
@bot.message_handler(commands=['budget'])
def budget_command(message):
    global budget_manager
    budget_manager = BudgetManager()
    bot.reply_to(message, "Please enter your budget in the format: /setbud G <amount>, B <amount>, F <amount>, W <amount>, M <amount>")

@bot.message_handler(func=lambda message: message.text.startswith('/setbud '))
def set_budget_command(message):
    try:
        global budget_manager
        budget_manager = BudgetManager()
        budget_manager.parse_message(message.text)
        bot.send_message(message.chat.id, f"Budget is set with:\n{budget_manager.get_budget_summary()}")
        bot.send_message(message.chat.id, f"Total budget messageset: {budget_manager.get_total_budget()}")

    except ValueError as e:
        # Error message in process_spend_command
        bot.send_message(message.chat.id, f"Error: {e}\n"
        "Please provide the information in the correct format:\n'/budget G <amount>, B <amount>, F <amount>, W <amount>, M <amount>")

@bot.message_handler(commands=['checkbud'])
def check_budget_command(message):
    str_out = check_budget()
    bot.reply_to(message, str_out)

bot.polling()

