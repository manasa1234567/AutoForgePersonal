from app.models.dashboard import DashboardData, ProgramSummary
from app.services.auth import User
from typing import List

async def get_dashboard_data_for_user(user: User) -> DashboardData:
    # Stub example returns static data; replace with DB and integrations
    return DashboardData(
        total_learners=150,
        active_programs=[
            ProgramSummary(program_id=1, name="Safety Training", completion_rate=75.5, assigned_courses=5, active=True),
            ProgramSummary(program_id=2, name="Compliance", completion_rate=60.0, assigned_courses=3, active=True)
        ],
        completion_rate_percent=68.3,
        upcoming_sessions_count=4,
        attendance_trend=[50, 55, 60, 58, 65],
        feedback_rating_avg=4.3,
        recent_activities=["Registered for Safety Training", "Completed Compliance Module 2"],
        top_performing_learners=["Alice", "Bob", "Charlie"],
        notifications=["New course available: Data Privacy", "Feedback survey due for Safety Training"]
    )
