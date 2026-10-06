from __future__ import annotations

import asyncio
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

        cloud_model_configured = any(
            os.getenv(name)
            for name in (
                "FOUNDRY_PROJECT_ENDPOINT",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_DEPLOYMENT",
            )
        )
        if cloud_model_configured:
            raise RuntimeError(
                "Cloud model analysis is configured but AZURE_CONTENT_SAFETY_ENDPOINT is missing; "
                "configure Azure Prompt Shields before enabling model-backed analysis"
            )

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
                    response = await self._shield_request(client,
                        f"{endpoint}/contentsafety/text:shieldPrompt",
                        params={"api-version": os.getenv("AZURE_PROMPT_SHIELDS_API_VERSION", "2024-09-01")},
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
            # Preserve safe provider diagnostics so a cloud failure can be
            # distinguished from an auth, endpoint, or API-version problem.
            # Never include request headers, tokens, or the configured endpoint.
            if isinstance(exc, httpx.HTTPStatusError):
                status = exc.response.status_code
                error_code = exc.response.headers.get("x-ms-error-code")
                diagnostic = f"HTTP {status}"
                if error_code:
                    diagnostic += f", Azure error code {error_code}"
                raise RuntimeError(
                    f"Azure Prompt Shields check failed ({diagnostic}); analysis stopped"
                ) from exc
            raise RuntimeError(f"Azure Prompt Shields check failed ({type(exc).__name__}); analysis stopped") from exc
        finally:
            await credential.close()

    @staticmethod
    async def _shield_request(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
        """Retry only transient provider failures, without skipping any chunk."""
        for attempt in range(3):
            response = None
            try:
                response = await client.post(url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in {408, 429, 500, 502, 503, 504} or attempt == 2:
                    raise
            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt == 2:
                    raise
            delay = float(2 ** attempt)
            if response is not None:
                retry_after = response.headers.get("Retry-After", "")
                try:
                    delay = max(delay, min(float(retry_after), 10.0))
                except ValueError:
                    pass
            await asyncio.sleep(delay)
        raise RuntimeError("Prompt Shields retry limit reached")

    async def deploy(self, build_id: str) -> dict[str, str]:
        raise RuntimeError(
            "Azure deployment is not configured. The Deployer Agent will not fabricate a deployment URL or smoke-test result."
        )
