from app.models.user import UserBase, UserRole
from datetime import datetime
from typing import Dict, Any

async def get_dashboard_for_user(user: UserBase) -> Dict[str, Any]:
    # Simplified stub with static data
    if user.role == UserRole.employee:
        return {
            "total_learners": 1,
            "active_programs": 2,
            "completion_rate_percent": 74.3,
            "upcoming_sessions": [
                {"id": 101, "title": "Intro to Compliance", "start": "2024-07-10T10:00:00Z"}
            ],
            "attendance_trend": [75, 80, 70, 74, 78],
            "feedback_rating_chart": [4, 3, 5, 4, 4],
            "recent_activities": [
                {"user": "John Doe", "activity": "Completed module 'Cybersecurity'", "date": "2024-07-01T12:00:00Z"}
            ],
            "top_performing_learners": [
                {"name": "John Doe", "completion": 98}
            ],
            "notifications": ["New program available: Data Ethics"],
            "quick_actions": ["Register for upcoming session"]
        }
    elif user.role == UserRole.manager:
        return {
            "team_learning_progress": 85.5,
            "attendance_stats": {"average": 80, "trend": [75, 78, 79, 82]},
            "completion_rates": 90,
            "feedback_trends": [4.2, 4.3, 4.5],
            "reports": ["Monthly Learning Summary", "Team Feedback Analysis"]
        }
    else:
        return {"message": "Dashboard data not implemented for this role."}
