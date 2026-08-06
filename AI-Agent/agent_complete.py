from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ===================== TOOL FUNCTIONS =====================

def search_flights(destination: str, departure_date: str, budget: float) -> str:
    """Simulate searching for flights"""
    return f"Found 8 flights to {destination} departing {departure_date}. Price range: ${budget * 0.7:.2f} - ${budget * 1.1:.2f}. Best options: Emirates ($450), FlyDubai ($380), Air Arabia ($320)"

def search_hotels(destination: str, check_in_date: str, nights: int, budget: float) -> str:
    """Simulate searching for hotels"""
    price_per_night = budget / nights
    return f"Found 12 hotels in {destination} for {nights} nights (check-in: {check_in_date}). Budget per night: ${price_per_night:.2f}. Options: Budget ($40-60/night), Mid-range ($80-120/night), Luxury ($150-250/night)"

def get_activities(destination: str, days: int, budget: float) -> str:
    """Get activities and attractions"""
    per_day_budget = budget / days
    activities = {
        "dubai": "Burj Khalifa ($25), Desert Safari ($80), Mall of the Emirates ($free), Beach ($free), Gold Souk ($free)"
    }
    return f"Top activities in {destination} ({days} days, ${per_day_budget:.2f}/day): {activities.get(destination.lower(), 'Various attractions available')}"

def calculate_total_cost(flights: float, hotels: float, activities: float) -> str:
    """Calculate and summarize total trip cost"""
    total = flights + hotels + activities
    return f"Trip cost breakdown - Flights: ${flights:.2f}, Hotels: ${hotels:.2f}, Activities: ${activities:.2f}, Total: ${total:.2f}"

# ===================== TOOL DEFINITIONS =====================

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for available flights to a destination. Returns flight options with prices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "The destination city (e.g., Dubai, Paris, New York)"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "Departure date in format YYYY-MM-DD"
                    },
                    "budget": {
                        "type": "number",
                        "description": "Maximum budget for flights in USD"
                    }
                },
                "required": ["destination", "departure_date", "budget"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Search for available hotels in a destination. Returns hotel options with prices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "The destination city"
                    },
                    "check_in_date": {
                        "type": "string",
                        "description": "Check-in date in format YYYY-MM-DD"
                    },
                    "nights": {
                        "type": "integer",
                        "description": "Number of nights to stay"
                    },
                    "budget": {
                        "type": "number",
                        "description": "Maximum budget for hotels in USD"
                    }
                },
                "required": ["destination", "check_in_date", "nights", "budget"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_activities",
            "description": "Get activities and attractions for a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "The destination city"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for activities"
                    },
                    "budget": {
                        "type": "number",
                        "description": "Budget for activities in USD"
                    }
                },
                "required": ["destination", "days", "budget"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_total_cost",
            "description": "Calculate total trip cost by summing up flights, hotels, and activities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flights": {
                        "type": "number",
                        "description": "Cost of flights in USD"
                    },
                    "hotels": {
                        "type": "number",
                        "description": "Cost of hotels in USD"
                    },
                    "activities": {
                        "type": "number",
                        "description": "Cost of activities in USD"
                    }
                },
                "required": ["flights", "hotels", "activities"]
            }
        }
    }
]

# ===================== EXECUTE TOOL =====================

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute the specified tool with given inputs"""
    try:
        if tool_name == "search_flights":
            return search_flights(
                destination=tool_input.get("destination", ""),
                departure_date=tool_input.get("departure_date", ""),
                budget=float(tool_input.get("budget", 0))
            )
        elif tool_name == "search_hotels":
            return search_hotels(
                destination=tool_input.get("destination", ""),
                check_in_date=tool_input.get("check_in_date", ""),
                nights=int(tool_input.get("nights", 0)),
                budget=float(tool_input.get("budget", 0))
            )
        elif tool_name == "get_activities":
            return get_activities(
                destination=tool_input.get("destination", ""),
                days=int(tool_input.get("days", 0)),
                budget=float(tool_input.get("budget", 0))
            )
        elif tool_name == "calculate_total_cost":
            return calculate_total_cost(
                flights=float(tool_input.get("flights", 0)),
                hotels=float(tool_input.get("hotels", 0)),
                activities=float(tool_input.get("activities", 0))
            )
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"

# ===================== MAIN AGENT LOOP =====================

def run_agent(user_prompt: str, max_iterations: int = 10):
    """Run the AI agent with the given prompt"""
    
    print("=" * 60)
    print("🤖 AI TRAVEL AGENT - POWERED BY GROQ MIXTRAL")
    print("=" * 60)
    print(f"\n👤 User Request: {user_prompt}\n")
    print("-" * 60)
    
    # Initialize conversation
    messages = [
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n[Iteration {iteration}]")
        
        try:
            # Call Groq API
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=messages,
                tools=tools,
                max_tokens=2048,
                temperature=0.7
            )
        except Exception as e:
            print(f"❌ API Error: {e}")
            break
        
        # Get response details
        finish_reason = response.choices[0].finish_reason
        assistant_message = response.choices[0].message
        
        # Print any text response
        if assistant_message.content:
            print(f"\n🤖 Agent: {assistant_message.content}")
        
        # Check if agent wants to call tools
        if finish_reason == "tool_calls" and assistant_message.tool_calls:
            print(f"\n🔧 Calling {len(assistant_message.tool_calls)} tool(s)...")
            
            # Add assistant's message to history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            # Process each tool call
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                print(f"   • {tool_name}({json.dumps(tool_args)})")
                
                # Execute tool
                result = execute_tool(tool_name, tool_args)
                print(f"     → {result[:100]}..." if len(result) > 100 else f"     → {result}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result
                })
            
            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        elif finish_reason == "stop":
            print("\n" + "=" * 60)
            print("✅ AGENT COMPLETED")
            print("=" * 60)
            if assistant_message.content:
                print(f"\n📋 Final Response:\n{assistant_message.content}")
            break
        
        else:
            print(f"\n⚠️ Unexpected finish reason: {finish_reason}")
            break
    
    if iteration >= max_iterations:
        print(f"\n⚠️ Reached maximum iterations ({max_iterations})")
    
    print("\n" + "=" * 60)

# ===================== RUN AGENT =====================

if __name__ == "__main__":
    user_input = "Plan a 3-day trip to Dubai with a total budget of $2000. Search for flights, hotels, and activities. Then calculate the total cost."
    run_agent(user_input)