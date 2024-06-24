class Income:
    def __init__(self, date, reason, amount, note) -> None:
        self.date = date
        self.reason = reason
        self.amount = amount
        self.note = note
    def __repr__(self) -> str:
        return ("Income:\n"
                f"Date: {self.date}\n"
                f"Earned from: {self.reason}\n"
                f"Amount: {self.amount}\n"
                f"Note: {self.note}.")
    

class Expense:
    def __init__(self,date , category, reason, amount, note) -> None:
        self.date = date
        self.category = category
        self.reason = reason
        self.amount = amount
        self.note = note
    def __repr__(self) -> str:
        category_dict = {
            "G" : "Groceries",
            "B" : "Bill and Housing",
            "F" : "Fun (Shopping and Eating out)",
            "W" : "Wellness (Education and Health)",
            "M" : "Miscellaneous"
        }
        return (f"Expense:\n"
                f"Date: {self.date}\n"
                f"Category: {category_dict[self.category]}\n"
                f"Spending Reason: {self.reason}\n"
                f"Amount: {self.amount}\n"
                f"Note: {self.note}")
