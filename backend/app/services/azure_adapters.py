from __future__ import annotations

import os

import httpx


class AzureAdapters:
    """Demo adapters that mirror the real Azure integration boundaries.

    Replace these methods with Microsoft Foundry/Azure SDK calls when the
    buildathon environment is provisioned. Keeping them behind one service
    boundary prevents Azure-specific code from leaking into orchestration.
    """

    async def content_safety_check(self, text: str) -> dict[str, bool | str]:
        endpoint = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT", "").rstrip("/")
        if endpoint:
            return await self._prompt_shields_check(endpoint, text)

        if os.getenv("FOUNDRY_PROJECT_ENDPOINT"):
            raise RuntimeError("Foundry analysis is configured but AZURE_CONTENT_SAFETY_ENDPOINT is missing")

        # Local-only fallback. Configure AZURE_CONTENT_SAFETY_ENDPOINT to use the
        # Azure Prompt Shields service before enabling cloud model analysis.
        suspicious_markers = ("ignore previous instructions", "disable security", "reveal system prompt")
        blocked = any(marker in text.lower() for marker in suspicious_markers)
        return {
            "blocked": blocked,
            "reason": "Prompt injection marker detected" if blocked else "Input accepted",
        }

    async def _prompt_shields_check(self, endpoint: str, text: str) -> dict[str, bool | str]:
        try:
            from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential
        except ImportError as exc:
            raise RuntimeError("Content Safety is configured but azure-identity is not installed") from exc

        if os.getenv("AUTOFORGE_IDENTITY_MODE", "").lower() == "managed_identity":
            client_id = os.getenv("AZURE_CLIENT_ID")
            credential = ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()
        else:
            credential = DefaultAzureCredential()

        try:
            token = await credential.get_token("https://cognitiveservices.azure.com/.default")
            headers = {"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"}
            # Prompt Shields accepts bounded text. Overlap preserves suspicious
            # instructions that happen to cross a chunk boundary.
            chunks = [text[index : index + 9_500] for index in range(0, len(text), 9_000)] or [""]
            async with httpx.AsyncClient(timeout=30.0) as client:
                for chunk in chunks:
                    response = await client.post(
                        f"{endpoint}/contentsafety/text:shieldPrompt",
                        params={"api-version": os.getenv("AZURE_PROMPT_SHIELDS_API_VERSION", "2024-02-15-preview")},
                        headers=headers,
                        json={
                            "userPrompt": "Extract requirements from the supplied engineering input.",
                            "documents": [chunk],
                        },
                    )
                    response.raise_for_status()
                    result = response.json()
                    prompt_attack = bool(result.get("userPromptAnalysis", {}).get("attackDetected"))
                    document_attacks = result.get("documentsAnalysis", [])
                    document_attack = any(
                        isinstance(item, dict) and bool(item.get("attackDetected"))
                        for item in document_attacks
                    )
                    if prompt_attack or document_attack:
                        return {"blocked": True, "reason": "Azure Prompt Shields detected a prompt injection attempt"}
            return {"blocked": False, "reason": "Azure Prompt Shields accepted the input"}
        except Exception as exc:
            raise RuntimeError(f"Azure Prompt Shields check failed ({type(exc).__name__}); analysis stopped") from exc
        finally:
            await credential.close()

    async def deploy(self, build_id: str) -> dict[str, str]:
        return {
            "deployment_url": f"https://internal-autoforge-{build_id}.azurecontainerapps.io",
        }
