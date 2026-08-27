import json
from datetime import datetime


def load_products():

    """
    Load product information from products.txt
    """

    with open("products.txt", "r", encoding="utf-8") as file:
        return file.read()


def save_lead(lead):

    """
    Save the processed lead into leads.json
    """

    try:
        with open("leads.json", "r", encoding="utf-8") as file:
            leads = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        leads = []

    # Add timestamp
    lead["processed_at"] = datetime.now().isoformat()

    # Add lead to database
    leads.append(lead)

    # Save back to file
    with open("leads.json", "w", encoding="utf-8") as file:
        json.dump(
            leads,
            file,
            indent=4
        )

    print("\nLead successfully saved.")