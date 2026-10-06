from app.models import User
from fastapi import Depends
from typing import Optional

async def get_user_from_token(token: str) -> Optional[User]:
    # This is a stub function simulating checking a token and returning a user
    # Real integration should validate with Microsoft Entra ID / Azure AD
    # For demo, we decode token and mock user data
    # Here, fake token string maps to a user
    fake_users = {
        "employee-token": User(
            id="u1", name="Alice Employee", email="alice@example.com", roles=["Employee"]
        ),
        "trainer-token": User(
            id="u2", name="Bob Trainer", email="bob@example.com", roles=["Trainer/Mentor"]
        ),
        "manager-token": User(
            id="u3", name="Carol Manager", email="carol@example.com", roles=["Manager"]
        ),
        "admin-token": User(
            id="u4", name="Dave Admin", email="dave@example.com", roles=["Administrator"]
        ),
    }
    return fake_users.get(token)
