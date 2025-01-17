import dash
from dash import dcc, html
import plotly.graph_objs as go
import dash_table
from Expense import Expense
from Income import income_summarize_monthly
from Budget import get_budget
from Data_Processing import overall_spending_vs_budget, category_spending_vs_budget
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Setup Dash app
app = dash.Dash(__name__)

# SQLAlchemy setup
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

# Visualization function
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

    a, total_income = income_summarize_monthly()

    # Dash Layout
    app.layout = html.Div([

        # Overall Summary
        html.Div([
            html.H1("Monthly Spending Summary", style={"textAlign": "center"}),
            dash_table.DataTable(
                columns=[{"name": "Metric", "id": "Metric"}, {"name": "Value", "id": "Value"}],
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
                style_table={"overflowX": "auto", "width": "100%", "margin": "auto"},
                style_header={"backgroundColor": "lightblue", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center", "padding": "10px", "fontSize": "14px"},
            ),
        ]),

        # Visualizations (Graphs)
        html.Div([

            # Graphs side by side
            html.Div([
                # Total Spending vs Total Budget (Pie Chart)
                dcc.Graph(
                    id="total-spending-vs-budget",
                    figure={
                        "data": [
                            go.Pie(
                                labels=["Spent", "Remaining"],
                                values=[total_spent, remaining_budget],
                                hole=0.1,
                                marker_colors=["orange", "lightblue"]
                            )
                        ],
                        "layout": go.Layout(
                            title="Total Spending vs Total Budget",
                            showlegend=True
                        )
                    },
                    style={"width": "48%", "display": "inline-block", "padding": "10px"}
                ),

                # Income vs Total Spending (Bar Chart)
                dcc.Graph(
                    id="total-spending-vs-income",
                    figure={
                        "data": [
                            go.Bar(
                                name="Income", 
                                x=["Income"], 
                                y=[total_income], 
                                marker_color="green"
                            ),
                            go.Bar(
                                name="Total Spending", 
                                x=["Spending"], 
                                y=[total_spent], 
                                marker_color="red"
                            )
                        ],
                        "layout": go.Layout(
                            title="Income vs Total Spending",
                            barmode="group",
                            xaxis={"title": "Category"},
                            yaxis={"title": "Amount ($)"},
                            showlegend=True
                        )
                    }, 
                     style={"height": "500px", "width": "700px"}
                ),
            ], style={"display": "flex", "justifyContent": "space-between", "flexWrap": "wrap", "marginTop": "20px"}),

            # Category Pie Charts (5 charts in a block, smaller size)
            html.Div([
                dcc.Graph(
                    id=f"category-pie-{i}",
                    figure={
                        "data": [
                            go.Pie(
                                labels=["Spent", "Remaining"],
                                values=[spent, max(0, budget - spent)],
                                hole=0.1,
                                marker_colors=["red" if spent > budget else "orange", "lightblue"]
                            )
                        ],
                        "layout": go.Layout(
                            title=f"{category_dict.get(cat, cat)}",
                            showlegend=True,
                        )
                    }, style={"height": "300px", "width": "300px"}
                )
                for i, (cat, spent, budget) in enumerate(zip(category_data[:, 0], category_spent, category_budget))
            ], style={
                "display": "flex", 
                "flexWrap": "wrap", 
                "justifyContent": "space-between", 
                "gap": "10px",  # Adds spacing between pie charts
                "marginTop": "20px"
            }),

            # Category-Specific Spending vs Budget (Bar Chart)
            html.Div(
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
                    },
                    style={"height": "500px", "width": "700px"}
                ),
                style={"width": "48%", "display": "inline-block", "padding": "10px"}
            ),

            # Remaining Budget by Category (Bar Chart)
            html.Div(
                dcc.Graph(
                    id="remaining-budget",
                    figure={
                        "data": [
                            go.Bar(
                                name="Remaining Budget",
                                x=categories,
                                y=category_remaining,
                                marker_color="lightgreen",
                                text=category_remaining,
                                textposition="outside"
                            )
                        ],
                        "layout": go.Layout(
                            title="Remaining Budget by Category",
                            xaxis={"title": "Categories"},
                            yaxis={"title": "Amount ($)", "range": [-300, 800]},
                            showlegend=True
                        )
                    },
                    style={"height": "500px", "width": "700px"}
                ),
                style={"width": "48%", "display": "inline-block", "padding": "10px"}
            )

        ])  # End of graphs container

    ])  # End of main layout

if __name__ == '__main__':
    visual_by_month()  # Initialize the layout

    # Run the app
    app.run_server(debug=True, port=8057)
