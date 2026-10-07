from app.api.auth_router import User

class AIAssistantService:

    @staticmethod
    async def process_query(query: str, user: User) -> str:
        # For demonstration, implement limited hardcoded commands
        q = query.lower()
        if "upcoming joiners" in q:
            return "Upcoming joiners: Alice, Bob, Carol."
        if "pending onboarding" in q:
            return "There are 3 pending onboarding tasks."
        if "generate onboarding tasks" in q:
            return "Onboarding tasks generation requested."
        if "incomplete documents" in q:
            return "Employees with incomplete documents: Dave, Eve."
        return "Sorry, I cannot help with that query yet."
