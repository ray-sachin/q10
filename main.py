# Question 10

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re
import json

# Enable CORS for all origins
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def normalize_department(raw_dept: str) -> str:
    raw = raw_dept.strip()
    # If it's short (likely an acronym), uppercase it (HR, IT, PR, etc.)
    if len(raw) <= 3 and raw.isalpha():
        return raw.upper()
    # Otherwise use title-case for readability
    return raw.title()

@app.get("/execute")
def execute(q: str = Query(..., description="Query from employee")):
    q_original = q.strip()
    q_lower = q_original.lower()

    # 1️⃣ Ticket Status
    ticket_match = re.search(r"status of ticket (\d+)", q_lower)
    if ticket_match:
        ticket_id = int(ticket_match.group(1))
        return {
            "name": "get_ticket_status",
            "arguments": json.dumps({"ticket_id": ticket_id})
        }

    # 2️⃣ Meeting Scheduling
    meeting_match = re.search(r"schedule a meeting on (\d{4}-\d{2}-\d{2}) at ([0-9:]+) in (.+)", q_lower)
    if meeting_match:
        date = meeting_match.group(1)
        time = meeting_match.group(2)
        # extract meeting room from original string to preserve case
        room_match = re.search(r"schedule a meeting on \d{4}-\d{2}-\d{2} at [0-9:]+ in (.+)", q_original, flags=re.IGNORECASE)
        meeting_room = room_match.group(1).strip().rstrip(".") if room_match else meeting_match.group(3).strip().rstrip(".")
        return {
            "name": "schedule_meeting",
            "arguments": json.dumps({
                "date": date,
                "time": time,
                "meeting_room": meeting_room
            })
        }

    # 3️⃣ Expense Balance
    expense_match = re.search(r"expense balance for employee (\d+)", q_lower)
    if expense_match:
        employee_id = int(expense_match.group(1))
        return {
            "name": "get_expense_balance",
            "arguments": json.dumps({"employee_id": employee_id})
        }

    # 4️⃣ Performance Bonus
    bonus_match = re.search(r"performance bonus for employee (\d+) for (\d{4})", q_lower)
    if bonus_match:
        employee_id = int(bonus_match.group(1))
        current_year = int(bonus_match.group(2))
        return {
            "name": "calculate_performance_bonus",
            "arguments": json.dumps({
                "employee_id": employee_id,
                "current_year": current_year
            })
        }

    # 5️⃣ Office Issue Reporting (flexible, capture from original text to preserve casing)
    issue_match = re.search(
        r"(\d+).*?(?:in|for the)\s+([a-zA-Z ]+?)\s+department",
        q_original,
        flags=re.IGNORECASE
    )
    if issue_match:
        issue_code = int(issue_match.group(1))
        raw_department = issue_match.group(2)
        department = normalize_department(raw_department)
        return {
            "name": "report_office_issue",
            "arguments": json.dumps({
                "issue_code": issue_code,
                "department": department
            })
        }

    # Default fallback
    return {"error": "Query not recognized. Please use a supported template."}
