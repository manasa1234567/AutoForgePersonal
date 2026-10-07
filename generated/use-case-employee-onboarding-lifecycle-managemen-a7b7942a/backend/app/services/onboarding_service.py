from typing import List, Optional
from app.schemas.onboarding import OnboardingTaskRead, OnboardingTaskUpdate, TaskStatus
from app.api.auth_router import User

# Dummy in-memory task list
_tasks = {}
_task_id_seq = 1

class OnboardingService:

    @staticmethod
    async def get_tasks_for_user(user: User) -> List[OnboardingTaskRead]:
        # Return all tasks assigned to a user based on role or username
        tasks_for_user = [task for task in _tasks.values() if task["assigned_to"] == user.username]
        return [OnboardingTaskRead(**task) for task in tasks_for_user]

    @staticmethod
    async def update_task_status(task_id: int, task_update: OnboardingTaskUpdate, user: User) -> Optional[OnboardingTaskRead]:
        task = _tasks.get(task_id)
        if not task or task["assigned_to"] != user.username:
            return None
        task["status"] = task_update.status
        task["remarks"] = task_update.remarks
        _tasks[task_id] = task
        return OnboardingTaskRead(**task)

    @staticmethod
    async def create_task(employee_id: int, task_name: str, assigned_to: str) -> OnboardingTaskRead:
        global _task_id_seq
        task_id = _task_id_seq
        _task_id_seq += 1
        task = {
            "task_id": task_id,
            "employee_id": employee_id,
            "task_name": task_name,
            "assigned_to": assigned_to,
            "status": TaskStatus.pending,
            "remarks": None
        }
        _tasks[task_id] = task
        return OnboardingTaskRead(**task)

    @staticmethod
    async def generate_onboarding_tasks(employee_id: int) -> None:
        # Predefined onboarding tasks for demo
        await OnboardingService.create_task(employee_id, "Email Account Creation", "ituser")
        await OnboardingService.create_task(employee_id, "Laptop Provision", "ituser")
        await OnboardingService.create_task(employee_id, "Manager Approval", "manageruser")
        await OnboardingService.create_task(employee_id, "Security Training", "ituser")
        
        # This demo simulates async creation - no return
