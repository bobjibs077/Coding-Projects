from Expenses import Expenses
import calendar
import datetime
import os
import langflow
from langflow import workflow


budget_file = "budget.txt"

def main():
    print(f"Running Expense Tracker")
    expense_file_path = "expenses.csv"

    budget = read_budget()
    print(f"Your budget for the month is £{budget:.2f}")

    if input("Do you want to update your budget? (y/n): ").strip().lower() == "y":
        budget = set_budget()
        write_budget(budget)

    while True:
        # Expense input
        expense = get_user_expense()
        if expense is None:
            print("No expense recorded. Exiting the program.")
            break

        # Save expense to a file
        save_expense_to_a_file(expense, expense_file_path)

        # Ask if the user wants to add more expenses
        if input("Do you want to add another expense? (y/n): ").strip().lower() != "y":
            break

    # Read expenses from a file and summarize
    summarise_expenses(expense_file_path, budget)


def set_budget():
    """Set budget for the month."""
    while True:
        try:
            budget = float(input("Enter your budget for the month: £").strip())
            return budget
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


def read_budget():
    """Read budget from file."""
    if not os.path.exists(budget_file):
        print("No budget found. Let's set one up.")
        budget = set_budget()
        write_budget(budget)
        return budget

    try:
        with open(budget_file, "r") as f:
            return float(f.read().strip())
    except (ValueError, FileNotFoundError):
        print("Invalid budget data found. Resetting the budget.")
        budget = set_budget()
        write_budget(budget)
        return budget


def write_budget(budget):
    """Write budget to a file."""
    with open(budget_file, "w") as f:
        f.write(f"{budget:.2f}")


def get_user_expense():
    """Get expense details from the user."""
    expense_name = input("Enter expense Name: ").strip()
    if not expense_name:
        print("Expense name cannot be empty. Please try again.")
        return get_user_expense()

    while True:
        try:
            expense_amount = float(input("Enter expense amount: £").strip())
            break
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")

    expense_categories = [
        "Food 🍔",
        "Home 🏠",
        "Transport 🚗",
        "Entertainment 🎮",
        "Health 🏥",
        "Education 📚",
        "Miscellaneous 🛒"
    ]

    while True:
        print("Select a category for your expense:")
        for i, category_name in enumerate(expense_categories):
            print(f"{i + 1}. {category_name}")
        try:
            selected_index = int(input("Enter the category number: ").strip())
            if 1 <= selected_index <= len(expense_categories):
                category = expense_categories[selected_index - 1]
                break
            else:
                print("Invalid category number. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    return Expenses(
        name=expense_name,
        amount=expense_amount,
        category=category
    )


def save_expense_to_a_file(expense: Expenses, expense_file_path):
    """Save an expense to a file."""
    print(f"Saving expense to file: {expense} to {expense_file_path}")
    with open(expense_file_path, "a", encoding="utf-8") as f:
        f.write(f"{expense.name}, {expense.amount}, {expense.category}\n")


def summarise_expenses(expense_file_path, budget):
    """Summarize expenses and display budget details."""
    print(f"Summarizing expenses from {expense_file_path}")
    expenses = []
    try:
        with open(expense_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                expense_name, expense_amount, expense_category = line.strip().split(",")
                expenses.append(Expenses(
                    name=expense_name,
                    amount=float(expense_amount),
                    category=expense_category
                ))
    except FileNotFoundError:
        print("No expenses recorded yet.")
        return


    amount_per_category = {}
    for expense in expenses:
        if expense.category in amount_per_category:
            amount_per_category[expense.category] += expense.amount
        else:
            amount_per_category[expense.category] = expense.amount

    print("Summary of expenses:")
    for category, amount in amount_per_category.items():
        print(f"{category}: £{amount:.2f}")

    total_spent = sum(expense.amount for expense in expenses)
    remaining_budget = budget - total_spent
    print(f"Total spent: £{total_spent:.2f}")
    print(f"Remaining budget: £{remaining_budget:.2f}")

    if total_spent > budget:
        print(red("You have exceeded your budget!"))
    else:
        print(green("You are within your budget!"))

    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = days_in_month - now.day
    daily_budget = remaining_budget / remaining_days if remaining_days > 0 else 0
    print(f"Remaining days in the month: {remaining_days}")
    print(f"Daily budget: £{daily_budget:.2f}")


def green(text):
    return f"\033[92m{text}\033[00m"


def red(text):
    return f"\033[91m{text}\033[00m"


if __name__ == "__main__":
    main()
