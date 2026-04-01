"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Standard school day blocks used to anchor structured activity schedules.
school_day_blocks = [
    {"name": "Period 1", "start_time": "08:55", "end_time": "09:45"},
    {"name": "Break", "start_time": "09:45", "end_time": "10:15"},
    {"name": "Period 2", "start_time": "10:15", "end_time": "11:05"},
    {"name": "Period 3", "start_time": "11:10", "end_time": "12:00"},
    {"name": "Lunch", "start_time": "12:00", "end_time": "13:00"},
    {"name": "Period 4", "start_time": "13:00", "end_time": "13:50"},
    {"name": "Period 5", "start_time": "13:55", "end_time": "14:45"},
    {"name": "After School", "start_time": "15:30", "end_time": "17:30"},
]

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "time_slots": [
            {"day": "Friday", "start_time": "15:30", "end_time": "17:00"}
        ],
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "time_slots": [
            {"day": "Tuesday", "start_time": "15:30", "end_time": "16:30"},
            {"day": "Thursday", "start_time": "15:30", "end_time": "16:30"},
        ],
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "time_slots": [
            {"day": "Monday", "start_time": "14:00", "end_time": "15:00"},
            {"day": "Wednesday", "start_time": "14:00", "end_time": "15:00"},
            {"day": "Friday", "start_time": "14:00", "end_time": "15:00"},
        ],
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "time_slots": [
            {"day": "Tuesday", "start_time": "16:00", "end_time": "17:30"},
            {"day": "Thursday", "start_time": "16:00", "end_time": "17:30"},
        ],
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "time_slots": [
            {"day": "Wednesday", "start_time": "15:30", "end_time": "17:00"},
            {"day": "Friday", "start_time": "15:30", "end_time": "17:00"},
        ],
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "time_slots": [
            {"day": "Thursday", "start_time": "15:30", "end_time": "17:00"}
        ],
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "time_slots": [
            {"day": "Monday", "start_time": "16:00", "end_time": "17:30"},
            {"day": "Wednesday", "start_time": "16:00", "end_time": "17:30"},
        ],
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "time_slots": [
            {"day": "Tuesday", "start_time": "15:30", "end_time": "16:30"}
        ],
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "time_slots": [
            {"day": "Friday", "start_time": "16:00", "end_time": "17:30"}
        ],
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


def parse_time_to_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def time_slots_overlap(first_slot: dict, second_slot: dict) -> bool:
    if first_slot["day"] != second_slot["day"]:
        return False

    first_start = parse_time_to_minutes(first_slot["start_time"])
    first_end = parse_time_to_minutes(first_slot["end_time"])
    second_start = parse_time_to_minutes(second_slot["start_time"])
    second_end = parse_time_to_minutes(second_slot["end_time"])
    return first_start < second_end and second_start < first_end


def find_conflicting_activities(activity_name: str) -> list[str]:
    activity = activities[activity_name]
    conflicts = []

    for other_name, other_activity in activities.items():
        if other_name == activity_name:
            continue

        has_overlap = any(
            time_slots_overlap(slot, other_slot)
            for slot in activity["time_slots"]
            for other_slot in other_activity["time_slots"]
        )
        if has_overlap:
            conflicts.append(other_name)

    return sorted(conflicts)


def serialize_activity(activity_name: str) -> dict:
    activity = activities[activity_name]
    spots_left = activity["max_participants"] - len(activity["participants"])
    return {
        **activity,
        "spots_left": spots_left,
        "availability": "Full" if spots_left <= 0 else "Open",
        "conflicts_with": find_conflicting_activities(activity_name),
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/schedule/blocks")
def get_school_day_blocks():
    return school_day_blocks


@app.get("/activities")
def get_activities():
    return {
        activity_name: serialize_activity(activity_name)
        for activity_name in activities
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
