from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re
import json

app = FastAPI()

# ✅ Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def normalize_department(raw_dept: str) -> str:
    """Normalize department name (e.g., 'it' -> 'IT', 'facilities' -> 'Facilities')."""
    raw = raw_dept.strip()
    if len(raw) <= 3 and raw.isalpha():
        return raw.upper()
    return raw.title()

@app.get("/execute")
def execute(q: str = Query(..., description="Query text from employee")):
    q_original = q.strip()
    q_lower = q_original.lower()

    # 1️⃣ Ticket Status
    match = re.search(r"status of ticket (\d+)", q_lower)
    if match:
        ticket_id = int(match.group(1))
        return {
            "name": "get_ticket_status",
            "arguments": json.dumps({"ticket_id": ticket_id})
        }

    # 2️⃣ Meeting Scheduling
    match = re.search(r"schedule a meeting on (\d{4}-\d{2}-\d{2}) at ([0-9:]+) in (.+)", q_lower)
    if match:
        date = match.group(1)
        time = match.group(2)
        # Extract exact case from original string
        room_match = re.search(r"schedule a meeting on \d{4}-\d{2}-\d{2} at [0-9:]+ in (.+)", q_original, flags=re.IGNORECASE)
        meeting_room = room_match.group(1).strip().rstrip(".") if room_match else match.group(3).strip().rstrip(".")
        return {
            "name": "schedule_meeting",
            "arguments": json.dumps({
                "date": date,
                "time": time,
                "meeting_room": meeting_room
            })
        }

    # 3️⃣ Expense Balance
    match = re.search(r"expense balance for employee (\d+)", q_lower)
    if match:
        employee_id = int(match.group(1))
        return {
            "name": "get_expense_balance",
            "arguments": json.dumps({"employee_id": employee_id})
        }

    # 4️⃣ Performance Bonus
    match = re.search(r"performance bonus for employee (\d+) for (\d{4})", q_lower)
    if match:
        employee_id = int(match.group(1))
        current_year = int(match.group(2))
        return {
            "name": "calculate_performance_bonus",
            "arguments": json.dumps({
                "employee_id": employee_id,
                "current_year": current_year
            })
        }

    # 5️⃣ Office Issue Reporting
    match = re.search(
        r"office issue (\d+).*?(?:in|for the)\s+([a-zA-Z ]+?)\s+department",
        q_original,
        flags=re.IGNORECASE
    )
    if match:
        issue_code = int(match.group(1))
        department = normalize_department(match.group(2))
        return {
            "name": "report_office_issue",
            "arguments": json.dumps({
                "issue_code": issue_code,
                "department": department
            })
        }

    # ❌ If no match found
    return {"error": "Query not recognized. Please use a supported template."}
