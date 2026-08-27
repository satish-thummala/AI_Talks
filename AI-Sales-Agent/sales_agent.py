import json
import os

from groq import Groq
from dotenv import load_dotenv

from tools import load_products, save_lead


# Load environment variables
load_dotenv()


# Create GROQ client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# Model to use
MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)


def process_lead(lead):

    # Load company product information
    products = load_products()

    # System instructions for our AI Sales Employee
    system_prompt = """
You are an AI Sales Employee working for a software company.

Your job is to analyze incoming sales leads and help the sales team
qualify and respond to those leads.

For every lead, you must:

1. Understand the customer's needs.
2. Identify the most appropriate product.
3. Score the lead from 0 to 100.
4. Categorize the lead as HOT, WARM, or COLD.
5. Explain why the lead received that score.
6. Recommend the next sales action.
7. Write a personalized sales email.

Use ONLY the product information provided to you.
Do not invent product features or pricing.

Return your response as valid JSON using exactly these fields:

{
    "customer_need": "...",
    "recommended_product": "...",
    "lead_score": 0,
    "lead_category": "HOT",
    "reason": "...",
    "next_action": "...",
    "sales_email": "..."
}

Do not include markdown or any text outside the JSON.
"""

    # Prepare the user prompt
    user_prompt = f"""
Here is the new sales lead:

{json.dumps(lead, indent=2)}

Here is our product information:

{products}

Analyze this lead and return the required JSON.
"""

    # Call the LLM
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    # Get the AI response
    content = response.choices[0].message.content

    # Convert JSON response into Python dictionary
    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        print("\nAI returned invalid JSON:")
        print(content)

        raise ValueError(
            "The AI response could not be converted to JSON."
        )

    # Add lead information to the result
    result["name"] = lead["name"]
    result["email"] = lead["email"]
    result["company"] = lead["company"]

    # Save the lead
    save_lead(result)

    return result