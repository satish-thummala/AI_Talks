from sales_agent import process_lead


lead = {
    "name": "John Smith",
    "email": "john@technova.com",
    "company": "TechNova",
    "industry": "Software",
    "employees": 120,
    "interest": "AI automation",
    "message": "We are looking to automate our customer support and reduce response time."
}


print("\n")
print("=" * 60)
print("AI SALES EMPLOYEE")
print("=" * 60)

print("\nNew lead received:")
print(f"Name: {lead['name']}")
print(f"Company: {lead['company']}")
print(f"Interest: {lead['interest']}")

print("\nProcessing lead...")

result = process_lead(lead)


print("\n")
print("=" * 60)
print("FINAL AI SALES EMPLOYEE REPORT")
print("=" * 60)

print(result)

print("\n")
print("=" * 60)