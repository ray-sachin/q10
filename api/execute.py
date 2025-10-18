# app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Function definitions
def get_ticket_status(ticket_id: int):
    return {"ticket_id": ticket_id, "status": "Open"}

def schedule_meeting(date: str, time: str, meeting_room: str):
    return {"date": date, "time": time, "meeting_room": meeting_room}

def get_expense_balance(employee_id: int):
    return {"employee_id": employee_id, "balance": 1250.75}

def calculate_performance_bonus(employee_id: int, current_year: int):
    return {"employee_id": employee_id, "year": current_year, "bonus": 5000.0}

def report_office_issue(issue_code: int, department: str):
    return {"issue_code": issue_code, "department": department, "status": "Reported"}

# Query mapping
@app.get("/execute")
def execute(q: str = Query(..., description="Pre-templatized question")):
    q = q.lower()
    
    # Ticket Status
    ticket_match = re.search(r"ticket (\d+)", q)
    if "status of ticket" in q and ticket_match:
        ticket_id = int(ticket_match.group(1))
        return {"name": "get_ticket_status", "arguments": json.dumps({"ticket_id": ticket_id})}

    # Schedule Meeting
    meeting_match = re.search(r"schedule a meeting on (\d{4}-\d{2}-\d{2}) at (\d{2}:\d{2}) in (.+)", q)
    if "schedule a meeting" in q and meeting_match:
        date, time, room = meeting_match.groups()
        return {"name": "schedule_meeting", "arguments": json.dumps({"date": date, "time": time, "meeting_room": room})}

    # Expense Balance
    expense_match = re.search(r"employee (\d+)", q)
    if "expense balance" in q and expense_match:
        employee_id = int(expense_match.group(1))
        return {"name": "get_expense_balance", "arguments": json.dumps({"employee_id": employee_id})}

    # Performance Bonus
    bonus_match = re.search(r"employee (\d+) for (\d{4})", q)
    if "performance bonus" in q and bonus_match:
        employee_id, year = bonus_match.groups()
        return {"name": "calculate_performance_bonus", "arguments": json.dumps({"employee_id": int(employee_id), "current_year": int(year)})}

    # Office Issue Reporting
    issue_match = re.search(r"issue (\d+) for the (.+) department", q)
    if "report office issue" in q and issue_match:
        issue_code, department = issue_match.groups()
        return {"name": "report_office_issue", "arguments": json.dumps({"issue_code": int(issue_code), "department": department})}

    return {"error": "Could not map query to a function"}

