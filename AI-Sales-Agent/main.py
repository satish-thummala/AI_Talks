from sales_agent import process_lead


# New sales lead
lead = {
    "name": "John Smith",
    "email": "john@technova.com",
    "company": "TechNova",
    "industry": "Software",
    "employees": 120,
    "interest": "AI automation",
    "message": "We are looking to automate our customer support and reduce response time."
}


# Send the lead to our AI Sales Employee
result = process_lead(lead)


# Display the result
print("\n" + "=" * 60)
print("AI SALES EMPLOYEE RESULT")
print("=" * 60)

print(f"\nLead: {lead['name']}")
print(f"Company: {lead['company']}")

print(f"\nLead Score: {result['lead_score']}/100")
print(f"Lead Category: {result['lead_category']}")

print(f"\nCustomer Need:")
print(result["customer_need"])

print(f"\nRecommended Product:")
print(result["recommended_product"])

print(f"\nReason:")
print(result["reason"])

print(f"\nRecommended Next Action:")
print(result["next_action"])

print("\n" + "-" * 60)
print("PERSONALIZED SALES EMAIL")
print("-" * 60)

print(result["sales_email"])

print("\n" + "=" * 60)