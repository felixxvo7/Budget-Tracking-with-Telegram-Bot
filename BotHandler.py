import telebot
from telebot import types
import os
from dash import dcc, html
from dotenv import load_dotenv
from Budget import Budget, BudgetManager, print_budget
from Visualization import visual_by_month
from Expense import Expense, expense_delete_by_id, expense_summarize_monthly, get_last_expense, spend_command
from Income import Income, earn_command, get_last_income, income_delete_by_id, income_summarize_monthly
from Data_Processing import check_budget, get_budget_message, overall_spending_vs_budget, category_spending_vs_budget
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

# Routine 1: Send a welcome message when the user starts a conversation
# Input: User starts the conversation with '/start', '/hello', or '/hi'
# Output: Sends a personalized welcome message with bot introduction
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
    
# Routine 2: Provide information about the bot's features
# Input: User sends '/about' command
# Output: Sends a detailed message about the bot’s functionality
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

# Routine 3: Provide a list of available commands
# Input: User sends '/help' command
# Output: Sends a list of commands to guide user on how to use the bot
@bot.message_handler(commands=['help'])
def send_welcome(message):
    start_text = "Welcome to the financial bot! Use the following commands to manage your finances: \n" \
                 "/about - Tell you more about the bot \n" \
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

# Routine 4: Ask the user to input spending data
# Input: User sends '/spend' command
# Output: Prompts user to input spending data with proper format using '/s'
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

# Routine 5: Process the spending data provided by the user
# Input: User sends a message starting with '/s' and provides spending data
# Output: Processes the data, saves the spending entry, and sends a formatted response along with the budget message
@bot.message_handler(func=lambda message: message.text.startswith('/s '))
def process_spend_command(message):
    try:
        global budget_manager
        new_expense = spend_command(message)
        category = new_expense.get_category()
        amount = new_expense.get_amount()
        report = get_budget_message(category)
        #send formatted message to user
        bot.send_message(message.chat.id,new_expense)
        bot.send_message(message.chat.id,report)
        bot.send_message(message.chat.id,"For more information about summary of your expenses: /expense_sum ")
    except ValueError as e:
        # Error message in process_spend_command
        bot.send_message(message.chat.id, f"Error: {e}\n"
        "Please provide the information in the correct format:\n'/s category, spending reason, amount, note'")

# Routine 6: Ask the user to input earning data
# Input: User sends '/earn' command
# Output: Prompts user to input earning data with proper format using '/e'
@bot.message_handler(commands=['earn'])
def prompt_earn(message):
    bot.send_message(message.chat.id, """Sure! Please use the /e command with the format:
     '/e earned from, amount, note (optional)'.
    """)

# Routine 7: Process the earning data provided by the user
# Input: User sends a message starting with '/e' and provides earning data
# Output: Processes the data, saves the earning entry, and sends a formatted response along with the income summary
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

# Routine 8: Provide a summary of expenses for the current month
# Input: User sends '/expense_sum' command
# Output: Sends a summary of expenses for the current month
@bot.message_handler(commands=['expense_sum'])
def expense_summary_command(message):
    bot.send_message(message.chat.id,expense_summarize_monthly())


# Routine 9: Provide a summary of earnings for the current month
# Input: User sends '/income_sum' command
# Output: Sends a summary of earnings for the current month
@bot.message_handler(commands=['income_sum'])
def expense_summary_command(message):
    bot.send_message(message.chat.id,income_summarize_monthly())

# Routine 10: Show the last recorded expenses
# Input: User sends '/last_expense' command
# Output: Sends the last 5 recorded expense entries
@bot.message_handler(commands=['last_expense'])
def expense_preview(message):
    last_expenses = get_last_expense()
    for expense in last_expenses:
        bot.send_message(message.chat.id, expense)

# Routine 11: Show the last recorded earnings
# Input: User sends '/last_income' command
# Output: Sends the last 5 recorded income entries
@bot.message_handler(commands=['last_income'])
def income_preview(message):
    last_earnings = get_last_income()
    for earning in last_earnings:
        bot.send_message(message.chat.id, earning)

# Routine 12: Provides options to view last 5 transactions for Expenses or Income
# Input: User sends '/view' command
# Output: Sends a brief message with options to view last 5 transactions of Expenses or Income
@bot.message_handler(commands=['view'])
def preview_command(message):
    str_out = """To view last 5 transactions of Expenses: /last_expense 
To view last 5 transactions of Income: /last_income """
    bot.send_message(message.chat.id, str_out)

# Routine 13: Deletes an expense or income entry by ID
# Input: User sends '/delete' command with data type (E or I) and ID of the entry to be deleted
# Output: Deletes the expense or income entry and sends confirmation message
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

# Routine 14: Starts the process to set a new budget
# Input: User sends '/budget' command
# Output: Sends a prompt to enter new budget values in a specific format
@bot.message_handler(commands=['budget'])
def budget_command(message):
    global budget_manager
    budget_manager = BudgetManager()
    get_report = print_budget()
    bot.send_message(message.chat.id, get_report)
    bot.send_message(message.chat.id, "Please enter your new budget in the format:\n/setbud G <amount>, B <amount>, F <amount>, W <amount>, M <amount>")

# Routine 15: Process and save the new budget set by the user
# Input: User sends the '/setbud' command with budget amounts
# Output: Saves the budget details and sends confirmation and budget summary
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
        
# Routine 16: Check and display the remaining budget for each category
# Input: User sends '/check_budget' command
# Output: Sends the remaining budget by category
@bot.message_handler(commands=['check_budget'])
def check_budget_command(message):
    str_out =  check_budget()
    bot.reply_to(message, str_out)
    bot.send_message(message.chat.id, " Go to /budget_summarize to see more detailed budget summarize.")

# Routine 17: Provide a comprehensive budget analysis (spending vs. budget)
# Input: User sends '/budget_summarize' command
# Output: Sends an analysis of overall spending and category-wise spending vs. budget
@bot.message_handler(commands=['budget_summarize'])
def check_budget_command(message):
    """Handles the /checkbud command to provide budget analysis."""
    overall_str, overall_data = overall_spending_vs_budget()
    category_str, category_data = category_spending_vs_budget()

    # Send the combined analysis message to the user
    bot.send_message(message.chat.id, overall_str)
    bot.send_message(message.chat.id, category_str)

# Routine 18: Provide a link to an external Dash app for financial summaries
# Input: User sends '/summarize' command
# Output: Sends a link to the Dash app for financial visual summaries
@bot.message_handler(commands=['summarize'])
def check_budget_command(message):
    visual_by_month()
    bot.send_message(message.chat.id, "Visit the Dash app for visual summaries: http://127.0.0.1:8057/")

# Start polling to receive messages from users
bot.polling()
    