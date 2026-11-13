
from research_agent import research_agent
from analyst_agent import analyst_agent
from strategy_agent import strategy_agent
from report_agent import report_agent


def manager_agent():

    print("\n================================")
    print("     MULTI-AGENT SYSTEM")
    print("================================")

    print("\n[Manager] Starting workflow...")

    # Step 1: Research
    print("\n[Manager] Assigning task to Research Agent")
    research_agent()

    # Step 2: Analysis
    print("\n[Manager] Assigning task to Analyst Agent")
    analyst_agent()

    # Step 3: Strategy
    print("\n[Manager] Assigning task to Strategy Agent")
    strategy_agent()

    # Step 4: Final Report
    print("\n[Manager] Assigning task to Report Agent")
    report = report_agent()

    print("\n[Manager] All agents completed successfully.")

    return report
