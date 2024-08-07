from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLAlchemy Base
Base = declarative_base()


#Represents a budget entry in the database.
"""
Attributes:
    id (int): Unique identifier for the budget entry.
    category (str): Category of the budget entry (e.g. "G" for Groceries).
    amount (float): Amount allocated to the budget category.
"""
class Budget(Base):
    __tablename__ = 'budget'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    #Initializes a new Budget instance.
    def __init__(self, category, amount):
        self.category = category
        self.amount = amount

# Initialize the database
engine = create_engine('sqlite:///budget.db')
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
# Create a Session
session = Session()

#Manages a budget by parsing user input, storing data in a database, and providing summary information.
class BudgetManager:
    category_list = ['G', 'B', 'F', 'W', 'M']

    def __init__(self):
        self.bud_list = []
        self.bud_category = []
        self.total_budget = 0
        self.bud_dict = {}

    #Parses a user-provided message to extract budget information.
    def parse_message(self, message):
        if not message or len(message) < 8:
            raise ValueError("Invalid message!")

        user_data = message[8:].split(', ')

        if len(user_data)!= 5:
            raise ValueError("Invalid number of fields!")

        for i in user_data:
            i = i.strip()
            budget = i.split(' ')
            if budget:
                if not budget[1].replace('.', '', 1).isdigit():
                    raise ValueError("Invalid amount!")
                self.bud_list.append(float(budget[1]))
                self.total_budget += float(budget[1])
                self.bud_category.append(budget[0])
            else:
                raise ValueError("Syntax error! Please try again.")

        if len(self.bud_category)!= len(self.category_list):
            raise ValueError("Incorrect number of categories! Please try again.")

        for i in range(len(self.category_list)):
            if self.bud_category[i]!= self.category_list[i]:
                raise ValueError("Categories are incorrect! Please try again.")
            
        self.bud_dict = dict(zip(self.bud_category,self.bud_list))

        # Save to database
        self.save_to_db()

    #Returns a summary of the budget in a message string format.
    def get_budget_summary(self):
        return (f"Groceries: {self.bud_list[0]}\n"
                f"Bill and Housing: {self.bud_list[1]}\n"
                f"Fun: {self.bud_list[2]}\n"
                f"Wellness: {self.bud_list[3]}\n"
                f"Miscellaneous: {self.bud_list[4]}")

    #Returns total budget
    def get_total_budget(self):
        return self.total_budget
    
    #Returns dictionary of the budget object carries
    def get_budget_dict(self):
        return self.bud_dict
    
    #store data in the database
    def save_to_db(self):
        # Clear existing data
        session.query(Budget).delete()

        for category, amount in self.bud_dict.items():
            budget_entry = Budget(category=category, amount=amount)
            session.add(budget_entry)

        session.commit()
    
#Returns amount of budget in setup of category dict and total budget amount
def get_budget():
    budget_category = {}
    budgets = session.query(Budget).all()
    total_amount = 0
    for budget in budgets:
        budget_category[budget.category] = budget.amount
        total_amount += budget.amount

    return budget_category, total_amount


    