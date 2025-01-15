import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog
from Expenses import Expenses
import os
import calendar
import datetime

budget_file = "budget.txt"
expense_file_path = "expenses.csv"

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("400x450")
        self.root.config(bg="#f4f4f4")  # Background color

        self.budget = self.read_budget()
        self.create_widgets()

    def create_widgets(self):
        # Configure a style for the widgets
        style = ttk.Style(self.root)
        style.configure('TButton', font=('Arial', 12), padding=6, relief="flat", background="#4CAF50", foreground="blue")
        style.configure('TLabel', font=('Arial', 12), background="#f4f4f4", foreground="blue")
        style.configure('TEntry', font=('Arial', 12), padding=6)

        # Budget display label
        self.budget_label = ttk.Label(self.root, text=f"Your budget for the month is: £{self.budget:.2f}")
        self.budget_label.grid(row=0, column=0, columnspan=2, pady=15, padx=20)

        # Update Budget button
        self.update_budget_button = ttk.Button(self.root, text="Update Budget", command=self.update_budget)
        self.update_budget_button.grid(row=1, column=0, columnspan=2, pady=10, padx=20)

        # Expense Name field
        self.expense_name_label = ttk.Label(self.root, text="Expense Name:")
        self.expense_name_label.grid(row=2, column=0, pady=10, padx=20, sticky="w")

        self.expense_name_entry = ttk.Entry(self.root)
        self.expense_name_entry.grid(row=2, column=1, pady=10, padx=20)

        # Expense Amount field
        self.expense_amount_label = ttk.Label(self.root, text="Expense Amount:")
        self.expense_amount_label.grid(row=3, column=0, pady=10, padx=20, sticky="w")

        self.expense_amount_entry = ttk.Entry(self.root)
        self.expense_amount_entry.grid(row=3, column=1, pady=10, padx=20)

        # Category field (dropdown)
        self.category_label = ttk.Label(self.root, text="Category:")
        self.category_label.grid(row=4, column=0, pady=10, padx=20, sticky="w")

        self.category_var = tk.StringVar(self.root)
        self.category_var.set("Food 🍔")

        self.category_menu = ttk.OptionMenu(self.root, self.category_var, 
            "Food 🍔", "Home 🏠", "Transport 🚗", "Entertainment 🎮", 
            "Health 🏥", "Education 📚", "Miscellaneous 🛒")
        self.category_menu.grid(row=4, column=1, pady=10, padx=20)

        # Add Expense button
        self.add_expense_button = ttk.Button(self.root, text="Add Expense", command=self.add_expense)
        self.add_expense_button.grid(row=5, column=0, columnspan=2, pady=10, padx=20)

        # Summary button
        self.summary_button = ttk.Button(self.root, text="Show Summary", command=self.summarise_expenses)
        self.summary_button.grid(row=6, column=0, columnspan=2, pady=10, padx=20)

    def update_budget(self):
        new_budget = simpledialog.askfloat("Set Budget", "Enter your new budget:", minvalue=0)
        if new_budget is not None:
            self.budget = new_budget
            self.write_budget(self.budget)
            self.budget_label.config(text=f"Your budget for the month is: £{self.budget:.2f}")

    def add_expense(self):
        expense_name = self.expense_name_entry.get().strip()
        if not expense_name:
            messagebox.showerror("Error", "Expense name cannot be empty!")
            return

        try:
            expense_amount = float(self.expense_amount_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid expense amount!")
            return

        category = self.category_var.get()

        expense = Expenses(name=expense_name, amount=expense_amount, category=category)
        self.save_expense_to_file(expense)
        messagebox.showinfo("Success", "Expense added successfully!")

    def summarise_expenses(self):
        expenses = self.load_expenses_from_file()
        amount_per_category = {}
        for expense in expenses:
            if expense.category in amount_per_category:
                amount_per_category[expense.category] += expense.amount
            else:
                amount_per_category[expense.category] = expense.amount

        summary = "Summary of expenses:\n"
        for category, amount in amount_per_category.items():
            summary += f"{category}: £{amount:.2f}\n"

        total_spent = sum(expense.amount for expense in expenses)
        remaining_budget = self.budget - total_spent
        summary += f"Total spent: £{total_spent:.2f}\n"
        summary += f"Remaining budget: £{remaining_budget:.2f}\n"

        if total_spent > self.budget:
            summary += "You have exceeded your budget!\n"
        else:
            summary += "You are within your budget!\n"

        now = datetime.datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        remaining_days = days_in_month - now.day
        daily_budget = remaining_budget / remaining_days if remaining_days > 0 else 0
        summary += f"Remaining days in the month: {remaining_days}\n"
        summary += f"Daily budget: £{daily_budget:.2f}"

        messagebox.showinfo("Expense Summary", summary)

    def load_expenses_from_file(self):
        expenses = []
        if os.path.exists(expense_file_path):
            with open(expense_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    expense_name, expense_amount, expense_category = line.strip().split(",")
                    expenses.append(Expenses(
                        name=expense_name,
                        amount=float(expense_amount),
                        category=expense_category
                    ))
        return expenses

    def save_expense_to_file(self, expense):
        with open(expense_file_path, "a", encoding="utf-8") as file:
            file.write(f"{expense.name}, {expense.amount}, {expense.category}\n")

    def read_budget(self):
        if not os.path.exists(budget_file):
            budget = simpledialog.askfloat("Set Budget", "Enter your initial budget:", minvalue=0)
            self.write_budget(budget)
            return budget

        with open(budget_file, "r") as file:
            return float(file.read().strip())

    def write_budget(self, budget):
        with open(budget_file, "w") as file:
            file.write(f"{budget:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
