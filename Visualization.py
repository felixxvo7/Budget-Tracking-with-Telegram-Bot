import dash
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
from datetime import datetime
import threading
#from BotHandler import bot  # Import your Telegram bot instance
from Expense import Expense
from Budget import get_budget
from Income import income_summarize_monthly
from Data_Processing import check_budget, get_budget_message, overall_spending_vs_budget, category_spending_vs_budget
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Setup
app = dash.Dash(__name__)

engine = create_engine('sqlite:///expenses.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

category_dict = {
    "G": "Groceries",
    "B": "Bill and Housing",
    "F": "Fun (Shopping and Eating out)",
    "W": "Wellness (Education and Health)",
    "M": "Miscellaneous"
}

def visual_by_month():
    """
    Visualizes the monthly spending and budget data.
    """
    # Get overall spending vs budget data
    overall_message, overall_data = overall_spending_vs_budget()

    # Get category-specific spending vs budget data
    category_message, category_data = category_spending_vs_budget()

    # Extract overall data
    total_budget = overall_data[0][0]
    total_spent = overall_data[0][1]
    remaining_budget = total_budget - total_spent

    # Extract category data
    categories = [category_dict.get(cat, cat) for cat in category_data[:, 0]]
    category_budget = category_data[:, 1]
    category_spent = category_data[:, 2]
    category_remaining = category_budget - category_spent

    # Dash Visualization
    app.layout = html.Div([
        html.H1("Monthly Spending Analysis", style={"textAlign": "center"}),

        # Total Spending vs Total Budget (Pie Chart)
        dcc.Graph(
            id="total-spending-vs-budget",
            figure={
                "data": [
                    go.Pie(
                        labels=["Spent", "Remaining"],
                        values=[total_spent, remaining_budget],
                        hole=0.3,
                        marker_colors=["yellow", "lightblue"]
                    )
                ],
                "layout": go.Layout(
                    title="Total Spending vs Total Budget",
                    showlegend=True
                )
            }
        ),

        # Category-Specific Spending vs Budget (Bar Chart)
        dcc.Graph(
            id="category-spending-vs-budget",
            figure={
                "data": [
                    go.Bar(name="Spent", x=categories, y=category_spent, marker_color="orange"),
                    go.Bar(name="Budget", x=categories, y=category_budget, marker_color="lightblue")
                ],
                "layout": go.Layout(
                    title="Category-Specific Spending vs Budget",
                    barmode="group",
                    xaxis={"title": "Categories"},
                    yaxis={"title": "Amount ($)"},
                    showlegend=True
                )
            }
        ),

        # Remaining Budget by Category (Bar Chart)
        dcc.Graph(
            id="remaining-budget",
            figure={
                "data": [
                    go.Bar(name="Remaining Budget", x=categories, y=category_remaining, marker_color="lightgreen")
                ],
                "layout": go.Layout(
                    title="Remaining Budget by Category",
                    xaxis={"title": "Categories"},
                    yaxis={"title": "Amount ($)"},
                    showlegend=True
                )
            }
        ),

        # Display Summary Messages
        html.Div([
            html.H3("Summary", style={"textAlign": "center"}),
            html.P(overall_message),
            html.P(category_message)
        ])
    ])


if __name__ == '__main__':
    # Call visual_by_month to set the layout
    visual_by_month()

    # Run the app
    app.run_server(debug=True, port=8057)
    

print("Bot is running... Access Dash visualization at http://127.0.0.1:8050/")
#bot.polling()
    