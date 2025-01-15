import streamlit as st
import plaid
from plaid.api import plaid_api
from plaid.model import *
import os
import datetime
import calendar
from Expenses import Expenses

# Plaid API Configuration
client = plaid.ApiClient(plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key=os.getenv('PLAID_CLIENT_ID')
))

plaid_api = plaid_api.PlaidApi(client)

budget_file = "budget.txt"
expense_file_path = "expenses.csv"

# Global variable to hold the current budget
current_budget = 0.0


def set_budget(budget):
    """Set budget for the month."""
    try:
        budget = float(budget)
        return budget
    except ValueError:
        st.error("Please enter a valid number for the budget.")
        return None


def read_budget():
    """Read budget from file."""
    if not os.path.exists(budget_file):
        st.info("No budget found. Let's set one up.")
        return None

    try:
        with open(budget_file, "r") as f:
            return float(f.read().strip())
    except (ValueError, FileNotFoundError):
        st.error("Invalid budget data found. Resetting the budget.")
        return None


def write_budget(budget):
    """Write budget to a file."""
    with open(budget_file, "w") as f:
        f.write(f"{budget:.2f}")


def get_user_expense(expense_name, expense_amount, expense_category):
    """Get expense details from the user."""
    try:
        expense_amount = float(expense_amount)
        expense = Expenses(name=expense_name, amount=expense_amount, category=expense_category)
        return expense
    except ValueError:
        st.error("Please enter a valid number for the expense amount.")
        return None


def save_expense_to_a_file(expense: Expenses, expense_file_path):
    """Save an expense to a file."""
    with open(expense_file_path, "a", encoding="utf-8") as f:
        f.write(f"{expense.name}, {expense.amount}, {expense.category}\n")


def summarise_expenses(expense_file_path, budget):
    """Summarize expenses and display budget details."""
    expenses = []
    try:
        with open(expense_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                expense_name, expense_amount, expense_category = line.strip().split(",")
                expenses.append(Expenses(name=expense_name, amount=float(expense_amount), category=expense_category))
    except FileNotFoundError:
        st.info("No expenses recorded yet.")
        return

    amount_per_category = {}
    for expense in expenses:
        if expense.category in amount_per_category:
            amount_per_category[expense.category] += expense.amount
        else:
            amount_per_category[expense.category] = expense.amount

    total_spent = sum(expense.amount for expense in expenses)
    remaining_budget = budget - total_spent

    st.write("### Summary of Expenses")
    for category, amount in amount_per_category.items():
        st.write(f"{category}: £{amount:.2f}")

    st.write(f"**Total Spent:** £{total_spent:.2f}")
    st.write(f"**Remaining Budget:** £{remaining_budget:.2f}")

    if total_spent > budget:
        st.error("You have exceeded your budget!")
    else:
        st.success("You are within your budget!")

    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = days_in_month - now.day
    daily_budget = remaining_budget / remaining_days if remaining_days > 0 else 0
    st.write(f"**Remaining days in the month:** {remaining_days}")
    st.write(f"**Daily Budget:** £{daily_budget:.2f}")


def get_transactions_from_plaid(access_token, start_date, end_date):
    """Fetch transactions from Plaid"""
    try:
        request = TransactionsGetRequest(access_token=access_token, start_date=start_date, end_date=end_date)
        response = plaid_api.transactions_get(request)
        transactions = response['transactions']
        return transactions
    except plaid.ApiException as e:
        st.error(f"Error fetching transactions: {e}")
        return []


def process_plaid_transactions():
    """Process transactions to match your expense categories"""
    access_token = st.text_input("Plaid Access Token:")
    start_date = st.date_input("Start Date", datetime.date(2025, 1, 1))
    end_date = st.date_input("End Date", datetime.date.today())

    if st.button("Fetch Transactions from Plaid"):
        transactions = get_transactions_from_plaid(access_token, start_date, end_date)
        if not transactions:
            return
        for txn in transactions:
            category = txn['category'][0] if txn['category'] else "Miscellaneous"
            expense = Expenses(name=txn['name'], amount=txn['amount'], category=category)
            save_expense_to_a_file(expense, expense_file_path)

        summarise_expenses(expense_file_path, current_budget)


def main():
    """Main function to run the streamlit app."""
    global current_budget

    # Display a welcome message
    st.title("Expense Tracker with Plaid")

    # Set or read the budget
    st.subheader("Set Your Budget for the Month")
    budget = st.text_input("Enter your monthly budget: £", value="0.0")
    if st.button("Set Budget"):
        current_budget = set_budget(budget)
        if current_budget is not None:
            write_budget(current_budget)
            st.success(f"Your budget for the month is £{current_budget:.2f}")

    # Manually add an expense
    st.subheader("Add an Expense")
    expense_name = st.text_input("Expense Name:")
    expense_amount = st.text_input("Amount (£):")
    expense_category = st.selectbox("Category:", ["Food 🍔", "Home 🏠", "Transport 🚗", "Entertainment 🎮", "Health 🏥", "Education 📚", "Miscellaneous 🛒"])

    if st.button("Add Expense"):
        expense = get_user_expense(expense_name, expense_amount, expense_category)
        if expense is not None:
            save_expense_to_a_file(expense, expense_file_path)
            st.success(f"Expense '{expense.name}' added successfully!")

    # Display summary of expenses
    if current_budget:
        summarise_expenses(expense_file_path, current_budget)

    # Fetch and process transactions from Plaid
    process_plaid_transactions()


if __name__ == "__main__":
    main()