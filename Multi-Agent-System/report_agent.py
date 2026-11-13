
from groq_client import get_llm_response
from shared_state import shared_state


def report_agent():

    print("\n[Report Agent] Preparing final report...")

    research = shared_state["research"]
    analysis = shared_state["analysis"]
    strategy = shared_state["strategy"]

    system_prompt = """
    You are a professional business report writer.

    Create a comprehensive business strategy report
    using the research, analysis, and strategy provided.

    Organize the report into these sections:

    1. Executive Summary
    2. Market Research
    3. Business Analysis
    4. Recommended Business Strategy
    5. Marketing and Customer Acquisition
    6. Potential Risks and Challenges
    7. Final Recommendations

    Use clear headings and professional language.
    Avoid repeating information unnecessarily.
    Do not introduce unsupported facts or figures.
    """

    user_prompt = f"""
    Prepare a concise business strategy report for
    opening an independent coffee shop in New York City.

    MARKET RESEARCH:
    {research[:2500]}

    BUSINESS ANALYSIS:
    {analysis[:2000]}

    BUSINESS STRATEGY:
    {strategy[:2000]}

    Include:
    1. Executive Summary
    2. Market Research
    3. Business Analysis
    4. Business Strategy
    5. Marketing Recommendations
    6. Risks and Challenges
    7. Final Recommendations

    Keep the report concise and practical.
    """
    
    result = get_llm_response(system_prompt, user_prompt)

    shared_state["report"] = result

    print("[Report Agent] Report completed.")

    return result
