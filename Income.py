from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
import pandas as pd

Base = declarative_base()
income_file = "exported_income.csv"


class Income(Base):
    __tablename__= "income"
    id = Column(Integer, primary_key=True,autoincrement=True)
    date = Column ("date", Date,nullable=False)
    source = Column("source", String, nullable= False )
    amount = Column("amount",Float, nullable=False)
    note = Column("note", String, nullable= True )

    def __init__(self, source, amount, note = None):
        self.source = source
        self.amount = amount
        self.date = date.today()
        self.note = None if note == "No additional note" else note
        


    def __repr__(self) -> str:
        return ("Income:\n"
                f"Date: {self.date}\n"
                f"Earned from: {self.source}\n"
                f"Amount: {self.amount}\n"
                f"Note: {self.note}.")
    

engine = create_engine('sqlite:///income.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_income(source,amount,note):
    new_income= Income(source=source,amount=amount,note=note)
    session.add(new_income)
    session.commit()
    return new_income

# Function to extract SQL table to CSV file
def export_income_to_csv():
    df = pd.read_sql('income', con=engine)
    df.to_csv(income_file, index=False)

def income_summarize_monthly():
   summary = session.query(
      func.strftime("%Y-%m",Income.date).label('month'),
      func.sum(Income.amount).label('total_amount')
   ).group_by('month').all()
 
   summary_str = "Monthly Income Summary by Category:\n"

   for month, total_amount in summary:
       summary_str += f"Month: {month}, Total: ${total_amount:.2f}\n"
       
   return summary_str


def get_last_earning():
    last_earning =  session.query(Income).order_by(Income.id.desc()).limit(5).all()
    return last_earning



def income_delete_by_id(id):
    delete = session.query(Income).filter(Income.id == id).first()
    if delete:
        session.delete(delete)
        session.commit()
        return f"Income with ID {id} deleted sucessfully."
    else:
        return f"No Income found with ID {id}."

def get_last_income():
    last_earnings =  session.query(Income).order_by(Income.id.desc()).limit(5).all()
    result= []
    for earning in last_earnings:
        result.append({
                f"Earning ID: {earning.id}\n"
                f"Date: {earning.date}\n"
                f"Earned from: {earning.source}\n"
                f"Amount: {earning.amount}\n"
                f"Note: {earning.note}."})
    return result
 

export_income_to_csv()