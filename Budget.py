
class Budget:
    def __init__(self, message):
        self.message = message
        self.bud_list = []
        self.bud_category = []
        self.category_list = ['G', 'B', 'F', 'W', 'M']
        self.total_budget = 0
        self.bud_dict = {}

    def parse_message(self):
        user_data = self.message.text[8:].split(', ')

        if len(user_data) != 5:
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

        if len(self.bud_category) != len(self.category_list):
            raise ValueError("Incorrect number of categories! Please try again.")

        for i in range(len(self.category_list)):
            if self.bud_category[i] != self.category_list[i]:
                raise ValueError("Categories are incorrect! Please try again.")
            
        self.bud_dict = dict(zip(self.bud_category,self.bud_list))

    def get_budget_summary(self):
        return (f"Groceries: {self.bud_list[0]}\n"
                f"Bill and Housing: {self.bud_list[1]}\n"
                f"Fun: {self.bud_list[2]}\n"
                f"Wellness: {self.bud_list[3]}\n"
                f"Miscellaneous: {self.bud_list[4]}")

    def get_total_budget(self):
        return self.total_budget
    
    def get_budget_dict(self):
        return self.bud_dict
    
