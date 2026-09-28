from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

DATA_FILE = "study_data.json"


@dataclass
class StudentProfile:
    name: str
    subject: str
    topics: List[str]
    days_remaining: int
    hours_per_day: float
    difficulty: str
    study_style: str
    plan: List[Dict[str, Any]] = field(default_factory=list)
    progress: Dict[str, str] = field(default_factory=dict)


class StudyPlannerApp:
    def __init__(self):
        self.student: StudentProfile | None = None
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.ai_available = bool(self.api_key and OpenAI)

    def display_menu(self):
        print("\n===== AI STUDENT STUDY ASSISTANT =====")
        print("1. Create Study Plan")
        print("2. View Study Plan")
        print("3. Update Task Status")
        print("4. View Progress")
        print("5. Get AI Recommendation")
        print("6. Exit")

    def get_student_input(self) -> StudentProfile:
        print("\nPlease enter your study details:\n")

        name = input("Student name: ").strip()
        subject = input("Subject name: ").strip()

        topics_input = input("Topics to study (separate with commas): ").strip()
        topics = [topic.strip() for topic in topics_input.split(",") if topic.strip()]

        if not topics:
            topics = ["General Review"]

        days_remaining = self.get_valid_int("Number of days remaining before the exam: ", min_value=1)
        hours_per_day = self.get_valid_float("Hours available for study each day: ", min_value=0.5)

        difficulty = ""
        while difficulty not in ["Easy", "Medium", "Hard"]:
            difficulty = input("Difficulty level (Easy / Medium / Hard): ").strip().title()
            if difficulty not in ["Easy", "Medium", "Hard"]:
                print("Please choose one of: Easy, Medium, Hard")

        study_style = ""
        while study_style not in ["Reading", "Practice", "Mixed"]:
            study_style = input("Preferred study style (Reading / Practice / Mixed): ").strip().title()
            if study_style not in ["Reading", "Practice", "Mixed"]:
                print("Please choose one of: Reading, Practice, Mixed")

        student = StudentProfile(
            name=name,
            subject=subject,
            topics=topics,
            days_remaining=days_remaining,
            hours_per_day=hours_per_day,
            difficulty=difficulty,
            study_style=study_style,
        )
        return student

    def get_valid_int(self, message: str, min_value: int) -> int:
        while True:
            try:
                value = int(input(message))
                if value < min_value:
                    print(f"Please enter a value greater than or equal to {min_value}.")
                    continue
                return value
            except ValueError:
                print("Please enter a valid whole number.")

    def get_valid_float(self, message: str, min_value: float) -> float:
        while True:
            try:
                value = float(input(message))
                if value < min_value:
                    print(f"Please enter a value greater than or equal to {min_value}.")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number.")

    def generate_plan(self, student: StudentProfile) -> List[Dict[str, Any]]:
        plan = []
        topic_cycle = student.topics[:]
        total_topics = len(topic_cycle)

        difficulty_multiplier = {
            "Easy": 1.0,
            "Medium": 1.3,
            "Hard": 1.6,
        }

        daily_hours = student.hours_per_day
        adjusted_hours = daily_hours * difficulty_multiplier[student.difficulty]

        for day_number in range(1, student.days_remaining + 1):
            daily_tasks = []
            topic_index = (day_number - 1) % total_topics
            main_topic = topic_cycle[topic_index]

            topic_hours = adjusted_hours * 0.45
            practice_hours = adjusted_hours * 0.25 if student.study_style in ["Practice", "Mixed"] else 0.15
            revision_hours = adjusted_hours * 0.2

            if main_topic:
                daily_tasks.append({
                    "type": "Topic",
                    "name": main_topic,
                    "time": round(topic_hours, 1),
                    "status": "Pending",
                })

            daily_tasks.append({
                "type": "Practice Questions",
                "name": "Practice Questions",
                "time": round(practice_hours, 1),
                "status": "Pending",
            })

            daily_tasks.append({
                "type": "Revision",
                "name": "Revision",
                "time": round(revision_hours, 1),
                "status": "Pending",
            })

            if student.study_style == "Reading":
                daily_tasks.insert(1, {
                    "type": "Reading",
                    "name": "Reading Notes",
                    "time": round(adjusted_hours * 0.20, 1),
                    "status": "Pending",
                })
            elif student.study_style == "Mixed":
                daily_tasks.insert(1, {
                    "type": "Concept Review",
                    "name": "Concept Review",
                    "time": round(adjusted_hours * 0.15, 1),
                    "status": "Pending",
                })

            plan.append({
                "day": day_number,
                "tasks": daily_tasks,
                "focus_topic": main_topic,
            })

        # Add a small set of high-priority topics
        student.plan = plan
        student.progress = self.initialize_progress(plan)
        return plan

    def initialize_progress(self, plan: List[Dict[str, Any]]) -> Dict[str, str]:
        progress = {}
        for day in plan:
            for task_index, task in enumerate(day["tasks"]):
                key = f"{day['day']}-{task_index}"
                progress[key] = "Pending"
        return progress

    def create_study_plan(self):
        student = self.get_student_input()
        plan = self.generate_plan(student)
        self.student = student
        self.save_data()
        self.display_plan(plan)

    def display_plan(self, plan: List[Dict[str, Any]]):
        print("\nYour Study Plan\n")
        for day_entry in plan:
            print(f"Day {day_entry['day']}")
            for task in day_entry["tasks"]:
                print(f"- {task['type']}: {task['name']} — {task['time']} hours")
            print()

    def view_plan(self):
        if self.student is None:
            print("No study plan found. Please create one first.")
            return
        self.display_plan(self.student.plan)

    def update_task_status(self):
        if self.student is None:
            print("No study plan found. Please create one first.")
            return

        print("\nUpdate task status")
        day_number = self.get_valid_int("Enter the day number: ", min_value=1)

        day_entry = None
        for item in self.student.plan:
            if item["day"] == day_number:
                day_entry = item
                break

        if day_entry is None:
            print("This day is not in your plan.")
            return

        print("Tasks for this day:")
        for index, task in enumerate(day_entry["tasks"]):
            print(f"{index + 1}. {task['type']}: {task['name']} ({task['time']} hours)")

        task_index = self.get_valid_int("Select the task number to update: ", min_value=1) - 1
        if task_index < 0 or task_index >= len(day_entry["tasks"]):
            print("Invalid task number.")
            return

        status = ""
        while status not in ["Completed", "Pending", "Skipped"]:
            status = input("Set status (Completed / Pending / Skipped): ").strip().title()
            if status not in ["Completed", "Pending", "Skipped"]:
                print("Please choose: Completed, Pending, or Skipped")

        key = f"{day_number}-{task_index}"
        self.student.progress[key] = status
        day_entry["tasks"][task_index]["status"] = status
        self.save_data()
        print(f"Task updated to: {status}")

    def calculate_progress(self) -> float:
        if self.student is None:
            return 0.0

        total_tasks = 0
        completed_tasks = 0

        for day in self.student.plan:
            for task in day["tasks"]:
                total_tasks += 1
                status = task.get("status", "Pending")
                if status == "Completed":
                    completed_tasks += 1

        if total_tasks == 0:
            return 0.0

        return (completed_tasks / total_tasks) * 100

    def view_progress(self):
        if self.student is None:
            print("No study plan found. Please create one first.")
            return

        percent = self.calculate_progress()
        print(f"\nStudy Progress: {percent:.0f}%")

        for day in self.student.plan:
            print(f"Day {day['day']}:")
            for task in day["tasks"]:
                print(f"- {task['type']}: {task['name']} — {task['status']}")
            print()

    def get_ai_recommendation(self):
        if self.student is None:
            print("No study plan found. Please create one first.")
            return

        if not self.ai_available:
            print("\nAI is not available because OPENAI_API_KEY is not set.")
            self.show_local_recommendation()
            return

        prompt = (
            f"You are a helpful study coach. The student is named {self.student.name}. "
            f"Their subject is {self.student.subject}. "
            f"They have {self.student.days_remaining} days left before the exam. "
            f"They study {self.student.hours_per_day} hours per day. "
            f"Their difficulty level is {self.student.difficulty}. "
            f"Their preferred study style is {self.student.study_style}. "
            f"Topics: {', '.join(self.student.topics)}. "
            f"Please give short recommendations about what to study next, which topic to prioritize, "
            f"how to use remaining time, and what to revise. Keep the answer simple and encouraging."
        )

        try:
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful academic study coach."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
            )
            recommendation = response.choices[0].message.content
            print("\nAI Recommendation:\n")
            print(recommendation)
        except Exception as error:
            print(f"\nAI request failed: {error}")
            self.show_local_recommendation()

    def show_local_recommendation(self):
        print("\nLocal Study Recommendation:\n")
        print(f"1. Focus on the most difficult topic first: {self.student.topics[0] if self.student else 'your main topic'}.")
        print("2. Prioritize active recall and practice questions.")
        print("3. Spend the last 30 minutes revising formulas, definitions, and mistakes.")
        print("4. Keep the final day for quick review and light practice, not heavy learning.")

    def save_data(self):
        try:
            data = {
                "student": {
                    "name": self.student.name if self.student else "",
                    "subject": self.student.subject if self.student else "",
                    "topics": self.student.topics if self.student else [],
                    "days_remaining": self.student.days_remaining if self.student else 0,
                    "hours_per_day": self.student.hours_per_day if self.student else 0,
                    "difficulty": self.student.difficulty if self.student else "",
                    "study_style": self.student.study_style if self.student else "",
                },
                "plan": self.student.plan if self.student else [],
                "progress": self.student.progress if self.student else {},
            }

            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        except Exception as error:
            print(f"Error saving data: {error}")

    def load_data(self):
        try:
            if not os.path.exists(DATA_FILE):
                return

            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not data:
                return

            student_data = data.get("student", {})
            if not student_data:
                return

            self.student = StudentProfile(
                name=student_data.get("name", ""),
                subject=student_data.get("subject", ""),
                topics=student_data.get("topics", []),
                days_remaining=student_data.get("days_remaining", 1),
                hours_per_day=student_data.get("hours_per_day", 1.0),
                difficulty=student_data.get("difficulty", "Medium"),
                study_style=student_data.get("study_style", "Mixed"),
                plan=data.get("plan", []),
                progress=data.get("progress", {}),
            )

            if self.student.plan:
                for day in self.student.plan:
                    for task_index, task in enumerate(day.get("tasks", [])):
                        key = f"{day['day']}-{task_index}"
                        if key in self.student.progress:
                            task["status"] = self.student.progress[key]

        except FileNotFoundError:
            print("No previous data found. Starting fresh.")
        except json.JSONDecodeError:
            print("Saved data is corrupted. Starting a new file.")
        except Exception as error:
            print(f"Error loading data: {error}")

    def run(self):
        self.load_data()

        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self.create_study_plan()
            elif choice == "2":
                self.view_plan()
            elif choice == "3":
                self.update_task_status()
            elif choice == "4":
                self.view_progress()
            elif choice == "5":
                self.get_ai_recommendation()
            elif choice == "6":
                print("\nThank you for using the AI Student Study Assistant. Goodbye!")
                break
            else:
                print("Invalid choice. Please select from 1 to 6.")

            input("\nPress Enter to continue...")


if __name__ == "__main__":
    app = StudyPlannerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Goodbye!")
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        sys.exit(1)
