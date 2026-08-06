from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

messages = [
    {
        "role": "user",
        "content": """You are a trip planning agent. Help plan a three-day trip to Dubai under $2000.
        
Consider:
- Flight costs
- Hotel costs (3 nights)
- Daily activities and food
- Transportation

Provide a detailed itinerary with estimated costs."""
    }
]

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages
)

print(response.choices[0].message.content)