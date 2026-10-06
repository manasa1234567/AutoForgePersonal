from typing import List
from app import models
import asyncio

# Dummy in-memory data

_assigned_programs = {
    "u1": [
        models.AssignedProgram(program_id="p1", program_name="Safety Training", completion_percentage=75.0, status="In Progress"),
        models.AssignedProgram(program_id="p2", program_name="Diversity Workshop", completion_percentage=100.0, status="Completed"),
    ]
}


async def employee_dashboard(user: models.User) -> models.DashboardData:
    # Compose dummy data
    return models.DashboardData(
        total_learners=2500,
        active_programs=25,
        completion_rate_percent=87.5,
        upcoming_sessions=["Safety Training - 2024-07-01", "Diversity Workshop - 2024-07-15"],
        attendance_trend_chart_data=[80, 82, 85, 87, 88],
        feedback_rating_chart_data=[4.2, 4.5, 4.0, 4.3],
        recent_activities=["Completed Diversity Workshop", "Submitted Feedback for Safety Training"],
        top_performing_learners=["Janet", "Mark", "Luke"],
        notifications=["Your next training starts soon"],
        quick_actions=["View Assigned Programs", "Submit Feedback"]
    )


async def trainer_dashboard(user: models.User) -> models.DashboardData:
    return models.DashboardData(
        total_learners=0,
        active_programs=0,
        completion_rate_percent=0.0,
        upcoming_sessions=["Safety Training - 2024-07-01"],
        attendance_trend_chart_data=[70, 75, 80, 85],
        feedback_rating_chart_data=[4.1, 4.4, 4.2],
        recent_activities=["Marked attendance for Safety Training"],
        top_performing_learners=["Alice Employee", "Bob Trainer"],
        notifications=["You have 1 session to manage"],
        quick_actions=["Mark Attendance", "Review Feedback"]
    )


async def manager_dashboard(user: models.User) -> models.DashboardData:
    return models.DashboardData(
        total_learners=0,
        active_programs=0,
        completion_rate_percent=0.0,
        upcoming_sessions=[],
        attendance_trend_chart_data=[90, 92, 93, 91],
        feedback_rating_chart_data=[4.3, 4.6, 4.7],
        recent_activities=["Reviewed Team Analytics"],
        top_performing_learners=["Team Lead 1", "Team Lead 2"],
        notifications=[],
        quick_actions=["View Team Analytics"]
    )


async def coordinator_dashboard(user: models.User) -> models.DashboardData:
    # Provide dummy coordinator relevant data
    return models.DashboardData(
        total_learners=0,
        active_programs=0,
        completion_rate_percent=0.0,
        upcoming_sessions=["Program Setup Due"],
        attendance_trend_chart_data=[],
        feedback_rating_chart_data=[],
        recent_activities=["Scheduled new program"],
        top_performing_learners=[],
        notifications=["New program approval required"],
        quick_actions=["Manage Programs"]
    )


async def admin_dashboard(user: models.User) -> models.DashboardData:
    # Admin has access to all data summarized
    return models.DashboardData(
        total_learners=3500,
        active_programs=45,
        completion_rate_percent=89.0,
        upcoming_sessions=["Quarterly Training Rollout"],
        attendance_trend_chart_data=[85, 87, 89, 90],
        feedback_rating_chart_data=[4.4, 4.5, 4.6, 4.7],
        recent_activities=["Created new user", "Updated program details"],
        top_performing_learners=["Top Learner 1", "Top Learner 2"],
        notifications=["System maintenance scheduled"],
        quick_actions=["Manage Users", "View Reports"]
    )


async def get_employee_assigned_programs(user_id: str) -> List[models.AssignedProgram]:
    return _assigned_programs.get(user_id, [])


async def save_feedback(user_id: str, feedback: models.FeedbackCreate) -> bool:
    # Pretend save
    await asyncio.sleep(0.1)  # simulate async DB
    return True


async def mark_attendance(user_id: str, attendance: models.AttendanceMark) -> bool:
    await asyncio.sleep(0.1)
    return True


async def manager_team_analytics(user_id: str) -> models.TeamAnalytics:
    return models.TeamAnalytics(
        attendance_percentage=92.5,
        completion_rate=88.0,
        feedback_trends=[4.3, 4.5, 4.6]
    )


async def admin_list_users() -> List[models.UserSummary]:
    return [
        models.UserSummary(id="u1", name="Alice Employee", email="alice@example.com", roles=["Employee"]),
        models.UserSummary(id="u2", name="Bob Trainer", email="bob@example.com", roles=["Trainer/Mentor"]),
        models.UserSummary(id="u4", name="Dave Admin", email="dave@example.com", roles=["Administrator"]),
    ]


async def admin_list_programs() -> List[models.ProgramSummary]:
    return [
        models.ProgramSummary(id="p1", name="Safety Training", description="Workplace safety training"),
        models.ProgramSummary(id="p2", name="Diversity Workshop", description="Inclusion and diversity training"),
    ]


async def admin_create_user(user_create: models.UserCreate) -> models.UserSummary:
    # Simulate create
    return models.UserSummary(id="newid", name=user_create.name, email=user_create.email, roles=user_create.roles)

