---
editor_options: 
  markdown: 
    wrap: 72
---

# Budget Tracking Dashboard

The Monthly Budget Tracker is a financial management application
designed to help users track their expenses, compare spending against a
predefined budget, and visualize financial insights via a Dash-powered
web interface.

Additionally, it integrates with a Telegram bot for real-time data entry
and summaries.

This is a Dash-based application that provides a budget tracking
dashboard. It allows users to visualize monthly spending, compare it
against budgets, and analyze income vs expenses.

## Features

**Telegram Bot**:

-   Enter income and expense data on the go.

-   Check your monthly budget summary using commands.

-   Access the Dash web app link for visualizations.

**Dash Visualization**:

-   Overall Spending vs. Budget:

    -   A pie chart showing total spending versus the remaining budget.

    -   Category-Specific Analysis: Bar charts showing category-wise
        budget versus spending.

    -   Remaining Budget Analysis:

        -   Bar chart with remaining budget for each category,
            displaying values on the bars.

**Database Integration**:

-   Stores budgets, expenses, and income in an SQLite database
    (expenses.db).

**Comprehensive Summaries**:

-   Provides text-based analysis of overspending, percentages spent, and
    remaining budgets.

**Visualizations**:

-   Pie charts for total spending and category-specific spending. -

-   Bar charts for income vs spending and remaining budget by category.

**Dash Tables**:

-   Displays detailed data for overall and category-specific budgets and
    spending.

## Technology Stack

-   **Backend**: SQLite database for storing expense data.
-   **Frontend**: Dash for interactive UI and Plotly for data
    visualizations.
-   **Data Processing**: Custom Python modules (`Expense`, `Income`,
    `Budget`, `Data_Processing`) for retrieving and calculating budget
    and spending metrics.

## Prerequisites

-   Python 3.8 or later
-   SQLite installed (if not already available)

## Installation

1.  Clone the repository: \`\`\`bash git clone
    <https://github.com/felixxvo7/Budget-Tracking-Dashboard.git>

Open the dashboard report application in your browser:

Navigate to <http://127.0.0.1:8057> in your web browser.

Set up the SQLite database:

Ensure you have a database file named expenses.db in the project root.
Populate the database with relevant tables and data using your schema. .

Troubleshooting Ensure the SQLite database (expenses.db) is in the
correct location and contains the necessary tables. If the app doesn't
load, check the console for errors and verify that all dependencies are
installed.

## Running the Application

1.  Start the Telegram Bot Run the bot to interact with it on Telegram:
    python BotHandler.py
2. Go to Telegram Bot through Telegram share link: https://t.me/trackingBudgetBot

3. Command Description:

/start Welcome message and bot introduction.

/about - Tell you more about the bot

/spend Log your spending data.

/earn Log your income data.

/setbud Set your monthly budget by categories.

/last_expense - To view last 5 transactions of Expense

/last_income - To view last 5 transactions of Income

/budget Shows the total budget and category-specific budgets.

/delete [id] Deletes an income entry by its ID.

/report Get a summary of your current month's financial data.

/help Lists all available commands and their descriptions.

/view - show last 5 transactions in either Expense data or Income data

/check_budget show me the remaining budget for all category current
month

/summarize Provides the Dash visualization link
(<http://127.0.0.1:8057/>).

4.  Start the Dash Visualization Run the Dash app to view
    visualizations: python Visualization/app.py
    -   Access the Dash app at <http://127.0.0.1:8057/>.

### License

This project is licensed under the MIT License.

### Author

Felix Vo

------------------------------------------------------------------------

Let me know if you need further assistance!
