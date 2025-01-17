---
editor_options: 
  markdown: 
    wrap: 72
---

# Budget Tracking Dashboard

This is a Dash-based application that provides a budget tracking
dashboard. It allows users to visualize monthly spending, compare it
against budgets, and analyze income vs expenses.

## Features

-   **Overall Spending Summary**: Displays total budget, total spent,
    percentage spent, and remaining budget.
-   **Category-Specific Analysis**: Provides a breakdown of spending vs
    budget across predefined categories (e.g., Groceries, Housing).
-   **Visualizations**:
    -   Pie charts for total spending and category-specific spending.
    -   Bar charts for income vs spending and remaining budget by
        category.
-   **Interactive Tables**: Displays detailed data for overall and
    category-specific budgets and spending.

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

### License

This project is licensed under the MIT License.

### Author

Felix Vo

------------------------------------------------------------------------

Let me know if you need further assistance!
