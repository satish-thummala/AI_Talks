
from groq_client import get_llm_response
from shared_state import shared_state


def strategy_agent():

    print("\n[Strategy Agent] Developing business strategy...")

    analysis_data = shared_state["analysis"]

    system_prompt = """
    You are an experienced business strategy consultant.

    Develop a practical business strategy based
    on the business analysis provided.

    Focus on:
    1. Coffee shop positioning
    2. Target customer strategy
    3. Product and pricing recommendations
    4. Marketing and customer acquisition
    5. Competitive differentiation
    6. Operational recommendations

    Provide actionable recommendations.
    Avoid inventing financial figures or
    unsupported market statistics.
    Clearly identify assumptions.
    """

    user_prompt = f"""
    Develop a business strategy for opening
    a new independent coffee shop in New York City.

    BUSINESS ANALYSIS:
    {analysis_data}

    Provide a structured and practical strategy.
    """

    result = get_llm_response(system_prompt, user_prompt)

    shared_state["strategy"] = result

    print("[Strategy Agent] Strategy completed.")

    return result
