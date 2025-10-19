from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re, json

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def normalize_department(raw: str) -> str:
    raw = raw.strip().rstrip(".")
    if len(raw) <= 3 and raw.isalpha():
        return raw.upper()
    return raw.title()

@app.get("/execute")
def execute(q: str = Query(..., description="Employee query text")):
    q_original = q.strip()
    q_lower = q_original.lower()

    # 1️⃣ Ticket Status
    m = re.search(r"status of ticket\s*(\d+)", q_lower)
    if m:
        ticket_id = int(m.group(1))
        return {
            "name": "get_ticket_status",
            "arguments": json.dumps({"ticket_id": ticket_id})
        }

    # 2️⃣ Schedule Meeting
    m = re.search(r"schedule a meeting on\s*(\d{4}-\d{2}-\d{2})\s*at\s*([0-9:]+)\s*(?:in|at)\s*(.+)", q_lower)
    if m:
        date, time = m.group(1), m.group(2)
        # preserve room case
        rm = re.search(r"schedule a meeting on\s*\d{4}-\d{2}-\d{2}\s*at\s*[0-9:]+\s*(?:in|at)\s*(.+)", q_original, flags=re.IGNORECASE)
        meeting_room = rm.group(1).strip().rstrip(".") if rm else m.group(3).strip().rstrip(".")
        return {
            "name": "schedule_meeting",
            "arguments": json.dumps({
                "date": date,
                "time": time,
                "meeting_room": meeting_room
            })
        }

    # 3️⃣ Expense Balance
    m = re.search(r"expense balance for employee\s*(\d+)", q_lower)
    if m:
        employee_id = int(m.group(1))
        return {
            "name": "get_expense_balance",
            "arguments": json.dumps({"employee_id": employee_id})
        }

    # 4️⃣ Performance Bonus
    m = re.search(r"performance bonus for employee\s*(\d+)\s*for\s*(\d{4})", q_lower)
    if m:
        employee_id, current_year = int(m.group(1)), int(m.group(2))
        return {
            "name": "calculate_performance_bonus",
            "arguments": json.dumps({
                "employee_id": employee_id,
                "current_year": current_year
            })
        }

    # 5️⃣ Office Issue
    m = re.search(r"office issue\s*(\d+).*?(?:for|in)\s*the\s*([a-zA-Z ]+?)\s*department", q_original, flags=re.IGNORECASE)
    if m:
        issue_code = int(m.group(1))
        department = normalize_department(m.group(2))
        return {
            "name": "report_office_issue",
            "arguments": json.dumps({
                "issue_code": issue_code,
                "department": department
            })
        }

    # ❌ Fallback (still valid JSON)
    return {
        "name": None,
        "arguments": "{}",
        "error": "Query not recognized. Make sure it matches one of the 5 templates."
    }
