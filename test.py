import dash
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
import dash_table
from Expense import Expense
from Budget import get_budget
from Data_Processing import overall_spending_vs_budget, category_spending_vs_budget
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
    overall_percentage_spent = overall_data[0][2]
    overspent_amount = overall_data[0][3]
    remaining_budget = total_budget - total_spent
    status_spent = (
        "You are within the budget."
        if overspent_amount == 0
        else f"OVERSPENT! (${overspent_amount:.2f} over)"
    )

    # Extract category data
    categories = [category_dict.get(cat, cat) for cat in category_data[:, 0]]
    category_budget = category_data[:, 1]
    category_spent = category_data[:, 2]
    category_remaining = category_budget - category_spent

    # Dash Layout
    app.layout = html.Div([
        # Overall Summary
        html.Div([
            html.H1("Monthly Spending Summary", style={"textAlign": "center"}),

            dash_table.DataTable(
                id="overall-summary-table",
                columns=[
                    {"name": "Metric", "id": "Metric"},
                    {"name": "Value", "id": "Value"}
                ],
                data=[
                    {"Metric": "Total Budget", "Value": f"${total_budget:.2f}"},
                    {"Metric": "Total Spent", "Value": f"${total_spent:.2f}"},
                    {"Metric": "Percentage Spent", "Value": f"{overall_percentage_spent:.2f}%"},
                    {"Metric": "Status", "Value": status_spent},
                ],
                style_table={"overflowX": "auto", "width": "60%", "margin": "auto"},
                style_header={"backgroundColor": "lightblue", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center", "padding": "10px", "fontSize": "16px"},
            ),
        ], style={"marginBottom": "30px"}),

        # Category Spending vs Budget
        html.Div([
            html.H3("Category Spending vs Budget", style={"textAlign": "center", "marginBottom": "10px"}),
            dash_table.DataTable(
                id="category-spending-table",
                columns=[
                    {"name": "Category", "id": "Category"},
                    {"name": "Budgeted", "id": "Budgeted"},
                    {"name": "Spent", "id": "Spent"},
                    {"name": "% Spent", "id": "% Spent"},
                    {"name": "Status", "id": "Status"}
                ],
                data=[
                    {
                        "Category": category_dict.get(cat, cat),
                        "Budgeted": f"${budget:.2f}",
                        "Spent": f"${spent:.2f}",
                        "% Spent": f"{(spent / budget) * 100:.2f}%",
                        "Status": (
                            f"OVERSPENT! (${spent - budget:.2f} over)" if spent > budget
                            else "Within Budget"
                        )
                    }
                    for cat, budget, spent in zip(category_data[:, 0], category_budget, category_spent)
                ],
                style_table={"overflowX": "auto", "width": "80%", "margin": "auto"},
                style_header={"backgroundColor": "lightblue", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center", "padding": "10px", "fontSize": "14px"},
            ),
        ]),

        # Visualizations (Graphs)
        html.Div([
            
            # Total Spending vs Total Budget (Pie Chart)
            dcc.Graph(
                id="total-spending-vs-budget",
                figure={
                    "data": [
                        go.Pie(
                            labels=["Spent", "Remaining"],
                            values=[total_spent, remaining_budget],
                            hole=0.3,
                            marker_colors=["orange", "lightblue"]
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
            )
        ])
    ])


if __name__ == '__main__':
    # Call visual_by_month to set the layout
    visual_by_month()

    # Run the app
    app.run_server(debug=True, port=8057)
