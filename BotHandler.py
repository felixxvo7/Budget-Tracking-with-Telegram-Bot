import telebot
from telebot import types
import os
from dotenv import load_dotenv
from Classes import Expense
from Classes import Income
from Methods import save_expense_to_file, save_income_to_file, summarize_by_category, summarize_total
from datetime import date
load_dotenv()
key = os.getenv('APIBUDGET')
bot_name = os.getenv('NAMEBUDGET')
BOT_TOKEN = key
BOT_USERNAME = bot_name
bot = telebot.TeleBot(BOT_TOKEN)
expense_file = "expenses.csv"
income_file = "income.csv"

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
    /report- Report the summary of transactions for this month until now
    /view  - give Google Sheet link to view data
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
        # split user data by commas
        user_data = message.text[3:].split(', ') 

        # check if 3 or 4 fields are provided
        if  len(user_data) not in [3, 4]:
            raise ValueError("Invalid number of fields!")

        # assign fields to variables
        category, reason, amount = user_data[:3]
        note = user_data[3] if len(user_data) == 4 else "No additional note" 
        
        # Handling error for Category field:
        if category not in ['G', 'B', 'F', 'W', 'M']:
            raise ValueError("""Invalid category. Category must be in: 
                G - Groceries
                B - Bill and Housing
                F - Fun (Shopping and Eating out)
                W - Wellness (Education and Health)
                M - Miscellaneous """) 

        # Handling error for Amount field:
        if not amount.replace('.','',1).isdigit():
            raise ValueError("Invalid amount!")

        
        #cast amount 
        amount = float(amount)

        #record date
        today = date.today()

        # create new expense:
        new_expense = Expense(
            date = today,
            category = category,
            reason = reason,
            amount = amount,
            note = note
        )

        save_expense_to_file(new_expense,expense_file)
        #send formatted message to user
        bot.send_message(message.chat.id,new_expense)
        summary = summarize_total("expense" , expense_file)
        bot.send_message(message.chat.id,f"Total Expenses: {summary}")
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
        # Get user data 
        user_data = message.text[3:].split(', ')
    
        # Check if the user provided 2 values
        if len(user_data) not in [2,3]:
            raise ValueError("Invalid number of fields!")
        
        # Split the user data into reason and amount
        reason, amount = user_data[:2]
        note = user_data[2] if len(user_data) == 3 else "No additional note"

        # Handling error for Amount field:
        if not amount.replace('.','',1).isdigit():
            raise ValueError("Invalid amount!")
        
        #cast amount 
        amount = float(amount)
        #record date
        today = date.today()

        # create new income:
        new_income = Income(
            date = today ,
            reason = reason,
            amount = amount,
            note = note
        )
        save_income_to_file(new_income,income_file)
        # Send a message to the user with the earned information
        bot.send_message(message.chat.id,new_income)
        income_summary = summarize_total("income" , income_file)
        bot.send_message(message.chat.id,f"Total Income: {income_summary}")
    except ValueError as e:
        # Send an error message to the user if they provided the wrong number of values
        bot.send_message(message.chat.id,f"Error: {e} \n" "Please provide the information in the correct format: '/e earned from, amount, note'.")

@bot.message_handler(commands=['summarize'])
def summary_command(message):
    list_category_summary = summarize_by_category(expense_file)
    category_dict = {
            "G" : "Groceries",
            "B" : "Bill and Housing",
            "F" : "Fun (Shopping and Eating out)",
            "W" : "Wellness (Education and Health)",
            "M" : "Miscellaneous"
        }
    for key, amount in list_category_summary.items():
        amount = float(amount)
        bot.send_message(message.chat.id,f"  {category_dict[key]}: {amount:.2f}")
    summary = summarize_total("expense" , expense_file)
    bot.send_message(message.chat.id,f"  Total expenses: {summary}")
        

bot.polling()

# database design! objevy relational manager, eg. PeeWee, SQLAlchemy -- Look at these two, and compare the advantages and disadvantages, talk to gpt