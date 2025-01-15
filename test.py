import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from langchain.agents import initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool
from astrapy import DataAPIClient
import uuid
from datetime import datetime
import warnings

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

# Configuration for LangFlow API
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "bdb0f7cd-b3c7-4bec-8603-9b0e7c07c3e8"
FLOW_ID = "ab57e78e-c9c3-48bd-8f6c-b135f268c020"
APPLICATION_TOKEN = "AstraCS:EBeTTwnBSCiRpMEmaLjwKBgE:8bb037dd710801a63ad701d0bc808d660f4a8b3f01cbc230bc2fd86485be6f32"
ENDPOINT = ""  # Set a specific endpoint if needed

# Astra DB Initialization
def initialize_db_client():
    TOKEN = "AstraCS:gJXYZyWwRPUUhNLbJgHerRZz:63e8a9fffd9740058dcafc67000c4dd6ce6aba2ac4cd24c363586ab4efb00eac"  
    DB_ENDPOINT = "https://c579acc2-85b3-4772-9ef6-116a588d7870-us-east-2.apps.astra.datastax.com"
    client = DataAPIClient(TOKEN)
    db = client.get_database_by_api_endpoint(DB_ENDPOINT)
    print(f"Connected to Astra DB: {db.list_collection_names()}")
    return db

def setup_db(db):
    budget_collection = db.collection("budget")
    expenses_collection = db.collection("expenses")
    return budget_collection, expenses_collection

# LangFlow Integration
def run_flow(message: str, endpoint: str, output_type: str = "chat", input_type: str = "chat",
             tweaks: Optional[dict] = None, application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks using LangFlow API.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# LangChain tools for interacting with Astra DB
@tool
def add_expense(user_id: str, expense_name: str, expense_amount: float, category: str):
    expenses_collection.create_document({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "expense_name": expense_name,
        "expense_amount": expense_amount,
        "category": category,
        "date": datetime.now().isoformat(),
    })
    return f"Expense '{expense_name}' added successfully."

@tool
def get_budget(user_id: str):
    doc = budget_collection.get_document(user_id)
    if doc.exists:
        return f"Your current budget is £{doc['budget_amount']:.2f}"
    return "No budget found. Please set one."

@tool
def set_budget(user_id: str, budget: float):
    budget_collection.create_or_update_document(
        user_id, {"user_id": user_id, "budget_amount": budget}
    )
    return f"Budget updated to £{budget:.2f}."

@tool
def summarize_expenses(user_id: str):
    docs = expenses_collection.find({"user_id": user_id})
    expenses = [{"name": doc["expense_name"], "amount": doc["expense_amount"], "category": doc["category"]} for doc in docs]
    total_spent = sum(e["amount"] for e in expenses)
    summary = f"Total spent: £{total_spent:.2f}\n"
    for expense in expenses:
        summary += f"- {expense['name']}: £{expense['amount']:.2f} ({expense['category']})\n"
    return summary

# LangFlow and LangChain Chatbot Workflow
def langflow_langchain_workflow():
    # Initialize Astra DB
    db = initialize_db_client()
    global budget_collection, expenses_collection
    budget_collection, expenses_collection = setup_db(db)

    # Define tools for the LangFlow agent
    tools = [add_expense, get_budget, set_budget, summarize_expenses]

    # Define a chatbot agent
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

    print("Finance Tracker Chatbot (LangFlow & LangChain)\nType 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Run LangFlow if input is for flow processing
        if user_input.startswith("flow:"):
            response = run_flow(user_input[5:], ENDPOINT, application_token=APPLICATION_TOKEN)
            print(f"LangFlow Bot: {response}")
        else:
            response = agent.run(user_input)
            print(f"LangChain Bot: {response}")

if __name__ == "__main__":
    langflow_langchain_workflow()
