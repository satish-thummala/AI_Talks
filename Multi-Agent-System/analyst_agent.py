
from groq_client import get_llm_response
from shared_state import shared_state


def analyst_agent():

    print("\n[Analyst Agent] Analyzing research findings...")

    research_data = shared_state["research"]

    system_prompt = """
    You are a professional business analyst.

    Analyze the market research provided to you.

    Focus on:
    1. Key market opportunities
    2. Target customer segments
    3. Competitive advantages
    4. Business risks and challenges
    5. Important business considerations

    Provide clear, practical conclusions.
    Base your analysis on the supplied research.
    Identify assumptions and information gaps.
    """

    user_prompt = f"""
    Analyze the following market research
    for opening a coffee shop in New York City.

    MARKET RESEARCH:
    {research_data}

    Provide a structured business analysis.
    """

    result = get_llm_response(system_prompt, user_prompt)

    shared_state["analysis"] = result

    print("[Analyst Agent] Analysis completed.")

    return result
