from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re
import json

app = FastAPI()

# ✅ Allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def normalize_department(raw_dept: str) -> str:
    """Normalize department name for consistent output."""
    raw = raw_dept.strip().rstrip(".")
    if len(raw) <= 3 and raw.isalpha():
        return raw.upper()
    return raw.title()

@app.get("/execute")
def execute(q: str = Query(..., description="Employee query text")):
    try:
        if not q or not isinstance(q, str):
            return {"error": "Invalid or missing query parameter 'q'."}

        q_original = q.strip()
        q_lower = q_original.lower()

        # --- 1️⃣ Ticket Status ---
        ticket_match = re.search(r"status of ticket\s+(\d+)", q_lower)
        if ticket_match:
            ticket_id = int(ticket_match.group(1))
            return {
                "name": "get_ticket_status",
                "arguments": json.dumps({"ticket_id": ticket_id})
            }

        # --- 2️⃣ Meeting Scheduling ---
        meeting_match = re.search(
            r"schedule a meeting on\s+(\d{4}-\d{2}-\d{2})\s+at\s+([0-9:]+)\s+in\s+(.+)", q_lower
        )
        if meeting_match:
            date = meeting_match.group(1)
            time = meeting_match.group(2)
            # extract meeting room with original casing
            room_match = re.search(
                r"schedule a meeting on\s+\d{4}-\d{2}-\d{2}\s+at\s+[0-9:]+\s+in\s+(.+)",
                q_original,
                flags=re.IGNORECASE
            )
            meeting_room = room_match.group(1).strip().rstrip(".") if room_match else meeting_match.group(3).strip().rstrip(".")
            return {
                "name": "schedule_meeting",
                "arguments": json.dumps({
                    "date": date,
                    "time": time,
                    "meeting_room": meeting_room
                })
            }

        # --- 3️⃣ Expense Balance ---
        expense_match = re.search(r"expense balance for employee\s+(\d+)", q_lower)
        if expense_match:
            employee_id = int(expense_match.group(1))
            return {
                "name": "get_expense_balance",
                "arguments": json.dumps({"employee_id": employee_id})
            }

        # --- 4️⃣ Performance Bonus ---
        bonus_match = re.search(r"performance bonus for employee\s+(\d+)\s+for\s+(\d{4})", q_lower)
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

        # --- 5️⃣ Office Issue Reporting ---
        issue_match = re.search(
            r"office issue\s+(\d+).*?(?:in|for the)\s+([a-zA-Z ]+?)\s+department",
            q_original,
            flags=re.IGNORECASE
        )
        if issue_match:
            issue_code = int(issue_match.group(1))
            department = normalize_department(issue_match.group(2))
            return {
                "name": "report_office_issue",
                "arguments": json.dumps({
                    "issue_code": issue_code,
                    "department": department
                })
            }

        # --- ❌ No match found ---
        return {
            "name": None,
            "arguments": "{}",
            "error": "Query not recognized. Expected one of the predefined templates."
        }

    except Exception as e:
        # Catch-all to ensure always valid JSON
        return {"name": None, "arguments": "{}", "error": str(e)}
