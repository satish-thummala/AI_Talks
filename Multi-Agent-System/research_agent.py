
from groq_client import get_llm_response
from shared_state import shared_state


def research_agent():

    print("\n[Research Agent] Starting market research...")

    system_prompt = """
    You are a professional business market researcher.

    Research the business opportunity of opening
    a new coffee shop in New York City.

    Focus on:
    1. Target customers
    2. Customer preferences
    3. Market opportunities
    4. Competitor landscape
    5. Potential business challenges

    Provide structured and practical findings.
    Clearly distinguish general market knowledge
    from assumptions that need local validation.
    Do not invent statistics or specific market data.
    """

    user_prompt = """
    Evaluate the opportunity for opening a new
    independent coffee shop in New York City.

    Provide useful findings for a business analyst.
    """

    result = get_llm_response(system_prompt, user_prompt)

    shared_state["research"] = result

    print("[Research Agent] Research completed.")

    return result
