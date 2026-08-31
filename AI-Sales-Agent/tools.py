import json
from datetime import datetime


def load_products():

    """
    Load product information from products.txt
    """

    with open("products.txt", "r", encoding="utf-8") as file:
        return file.read()

def score_lead(company, employees, interest):
    """
    Calculate a simple lead score based on
    company size and buying interest.
    """

    score = 0

    # Company size
    if employees >= 100:
        score += 40
    elif employees >= 50:
        score += 25
    else:
        score += 10

    # Buying interest
    interest_lower = interest.lower()

    if "ai" in interest_lower or "automation" in interest_lower:
        score += 40
    elif "software" in interest_lower:
        score += 25
    else:
        score += 10

    # Convert score into category
    if score >= 70:
        category = "HOT"
    elif score >= 40:
        category = "WARM"
    else:
        category = "COLD"

    return {
        "score": score,
        "category": category
    }

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