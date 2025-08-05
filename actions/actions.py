from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

import os
import requests
import sqlite3
from datetime import datetime

# -------------------------
# Docker-aware configuration
# -------------------------
# When mock API runs on host machine: http://host.docker.internal:8000
# If you later dockerize the mock API service as "mock_api", set DOCTOR_API_BASE=http://mock_api:8000 in docker-compose.
DOCTOR_API_BASE = os.getenv("DOCTOR_API_BASE", "http://host.docker.internal:8000")
DB_PATH = os.getenv("DB_PATH", "/app/user_logs.db")


# -------------------------
# DB helpers
# -------------------------
def ensure_db() -> None:
    """Create logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            intent TEXT,
            user_message TEXT,
            department TEXT,
            date TEXT,
            time TEXT,
            doctor TEXT,
            symptom TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_to_db(intent: str, user_message: str, slots: Dict[Text, Any]) -> None:
    """Insert one interaction row into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO logs (timestamp, intent, user_message, department, date, time, doctor, symptom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            intent,
            user_message,
            slots.get("department"),
            slots.get("preferred_date"),
            slots.get("preferred_time"),
            slots.get("doctor_name"),
            slots.get("symptom"),
        ),
    )
    conn.commit()
    conn.close()


# Ensure table exists on import
ensure_db()


# -------------------------
# Actions
# -------------------------
class ActionCheckAppointment(Action):
    def name(self) -> Text:
        return "action_check_appointment"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="You have an appointment with Dr. Sharma on Monday at 10 AM."
        )

        log_to_db(
            intent=tracker.latest_message.get("intent", {}).get("name"),
            user_message=tracker.latest_message.get("text"),
            slots=tracker.slots,
        )
        return []


class ValidateBookingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_booking_form"

    def validate_department(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        valid_departments = [
            "cardiology",
            "neurology",
            "dermatology",
            "orthopedics",
            "pediatrics",
        ]
        if isinstance(slot_value, str) and slot_value.lower() in valid_departments:
            return {"department": slot_value}
        dispatcher.utter_message(
            text=(
                "Sorry, we don't have that department. "
                "Please choose from Cardiology, Neurology, Dermatology, Orthopedics, or Pediatrics."
            )
        )
        return {"department": None}

    def validate_preferred_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        # Add real date validation if needed
        return {"preferred_date": slot_value}

    def validate_preferred_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        # Add real time validation if needed
        return {"preferred_time": slot_value}


class ActionSubmitAppointment(Action):
    def name(self) -> Text:
        return "action_submit_appointment"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[EventType]:
        department = tracker.get_slot("department")
        date = tracker.get_slot("preferred_date")
        time = tracker.get_slot("preferred_time")

        dispatcher.utter_message(
            text=f"Your appointment for {department} has been booked on {date} at {time}."
        )

        log_to_db(
            intent=tracker.latest_message.get("intent", {}).get("name"),
            user_message=tracker.latest_message.get("text"),
            slots=tracker.slots,
        )
        return []


class ActionDoctorInfo(Action):
    def name(self) -> Text:
        return "action_doctor_info"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        doctor_name = tracker.get_slot("doctor_name")

        if doctor_name:
            doctor_name_cleaned = doctor_name.strip().title()
            if not doctor_name_cleaned.startswith("Dr."):
                doctor_name_cleaned = f"Dr. {doctor_name_cleaned}"

            try:
                resp = requests.get(
                    f"{DOCTOR_API_BASE}/api/doctors/{doctor_name_cleaned}", timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    dispatcher.utter_message(text=data.get("info"))
                else:
                    dispatcher.utter_message(
                        text=f"Sorry, I couldn't find details for {doctor_name_cleaned}."
                    )
            except Exception as e:
                # Optional: log error to console for debugging
                print(f"[ERROR] Doctor info API error: {e}")
                dispatcher.utter_message(
                    text="Something went wrong while fetching the doctor info."
                )
        else:
            # Ensure you have 'utter_ask_doctor' defined in domain.yml
            dispatcher.utter_message(response="utter_ask_doctor")

        log_to_db(
            intent=tracker.latest_message.get("intent", {}).get("name"),
            user_message=tracker.latest_message.get("text"),
            slots=tracker.slots,
        )
        return []


class ActionSymptomCheck(Action):
    def name(self) -> Text:
        return "action_symptom_check"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        symptom = next(tracker.get_latest_entity_values("symptom"), None)

        if symptom:
            suggestions = {
                "headache": "Drink plenty of water and rest. If persistent, consult a doctor.",
                "fever": "Stay hydrated and take paracetamol. See a doctor if fever lasts more than 2 days.",
                "nauseous": "Eat light meals and rest. Ginger tea may help.",
                "back pain": "Apply a hot compress and avoid heavy lifting. Visit orthopedics if severe.",
                "stomach ache": "Try bland foods and stay hydrated. Avoid spicy items.",
                "cough": "Drink warm fluids and avoid cold drinks.",
                "sore throat": "Gargle with salt water and drink warm tea.",
                "dizzy": "Sit or lie down, drink water, and avoid sudden movements.",
                "chest pain": "This could be serious — please seek immediate medical help.",
                "cold": "Rest, stay hydrated, and take steam inhalation.",
                "flu": "Rest, fluids, and monitor temperature regularly.",
                "fatigue": "Ensure good sleep, eat nutritious meals, and reduce stress.",
            }
            suggestion = suggestions.get(
                symptom.lower(),
                f"Please consult a physician for advice on {symptom}.",
            )
            dispatcher.utter_message(text=f"For {symptom}, {suggestion}")

            log_to_db(
                intent=tracker.latest_message.get("intent", {}).get("name"),
                user_message=tracker.latest_message.get("text"),
                slots=tracker.slots,
            )
        else:
            dispatcher.utter_message(
                text="Please describe your symptom so I can help."
            )

        return []


class ActionLogHandover(Action):
    def name(self) -> Text:
        return "action_log_handover"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Connecting you to a human representative...")

        log_to_db(
            intent=tracker.latest_message.get("intent", {}).get("name"),
            user_message=tracker.latest_message.get("text"),
            slots=tracker.slots,
        )
        return []
