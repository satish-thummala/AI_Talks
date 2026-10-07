from models import ChoiceResult, ScoreResult, NoulResult
from sample_data import tickets


ticket = tickets[0]

print("Customer Support Ticket")
print("-----------------------")
print(ticket["message"])

request_type = ChoiceResult(
    value="refund",
    probabilities={
        "refund": 0.94,
        "information": 0.04,
        "technical": 0.02
    }
)

print("\nChoice Result")
print("-------------")
print("Request Type:", request_type.value)
print("Probabilities:", request_type.probabilities)

frustration = ScoreResult(
    value=2,
    probabilities={
        0: 0.05,
        1: 0.20,
        2: 0.75
    }
)

print("\nScore Result")
print("------------")
print("Frustration:", frustration.value)
print("Probabilities:", frustration.probabilities)

urgency = NoulResult(
    value=0.96
)

print("\nNoul Result")
print("-----------")
print("Urgency:", urgency.value)

print("\n==========================")
print("STRUCTURED AI RESULTS")
print("==========================")

print("Request Type :", request_type.value)
print("Frustration  :", frustration.value)
print("Urgency      :", urgency.value)

if urgency.value > 0.8 and frustration.value >= 2:
    priority = "HIGH"
else:
    priority = "NORMAL"


if request_type.value == "refund":
    team = "Billing"
else:
    team = "Customer Support"

print("\n==========================")
print("BUSINESS DECISION")
print("==========================")

print("Team     :", team)
print("Priority :", priority)