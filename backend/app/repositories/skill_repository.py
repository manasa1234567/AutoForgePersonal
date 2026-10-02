from __future__ import annotations

from typing import Protocol

from ..models.schemas import SkillRecipe


class SkillRepository(Protocol):
    """Storage boundary for governed skill recipes."""

    def list(self) -> list[SkillRecipe]: ...

    def get(self, recipe_id: str) -> SkillRecipe: ...

    def save(self, recipe: SkillRecipe) -> None: ...


class InMemorySkillRepository:
    """Local adapter; seeded recipes and decisions reset when the API restarts."""

    def __init__(self, recipes: list[SkillRecipe]) -> None:
        self._recipes = {recipe.id: recipe for recipe in recipes}

    def list(self) -> list[SkillRecipe]:
        return list(self._recipes.values())

    def get(self, recipe_id: str) -> SkillRecipe:
        try:
            return self._recipes[recipe_id]
        except KeyError as exc:
            raise KeyError(f"Skill recipe '{recipe_id}' not found") from exc

    def save(self, recipe: SkillRecipe) -> None:
        self._recipes[recipe.id] = recipe
