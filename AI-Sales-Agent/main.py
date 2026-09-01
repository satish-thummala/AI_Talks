from sales_agent import process_lead


# --------------------------------------------------
# HOT LEAD
# --------------------------------------------------

hot_lead = {
    "name": "John Smith",
    "email": "john@technova.com",
    "company": "TechNova",
    "industry": "Software",
    "employees": 120,
    "interest": "AI automation",
    "message": "We are looking to automate our customer support and reduce response time.",
    "preferred_meeting_date": "2026-09-03",
    "preferred_meeting_time": "10:00 AM"
}


# --------------------------------------------------
# COLD LEAD
# --------------------------------------------------

cold_lead = {
    "name": "Sarah Johnson",
    "email": "sarah@smallshop.com",
    "company": "SmallShop",
    "industry": "Retail",
    "employees": 5,
    "interest": "General information",
    "message": "I would like to learn more about your company."
}


# --------------------------------------------------
# PROCESS HOT LEAD
# --------------------------------------------------

print("\n")
print("=" * 60)
print("PROCESSING HOT LEAD")
print("=" * 60)

print(f"\nName: {hot_lead['name']}")
print(f"Company: {hot_lead['company']}")

hot_result = process_lead(hot_lead)

print("\nFINAL RESULT:")
print(hot_result)


# --------------------------------------------------
# PROCESS COLD LEAD
# --------------------------------------------------

print("\n")
print("=" * 60)
print("PROCESSING COLD LEAD")
print("=" * 60)

print(f"\nName: {cold_lead['name']}")
print(f"Company: {cold_lead['company']}")

cold_result = process_lead(cold_lead)

print("\nFINAL RESULT:")
print(cold_result)