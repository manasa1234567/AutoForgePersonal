from __future__ import annotations

import base64
import os
import re
import time
from urllib.parse import quote

import httpx

from ..models.schemas import BuildState


class GitHubPublisher:
    """Publish reviewed build artifacts on a new GitHub feature branch."""

    api = "https://api.github.com"

    async def publish(self, build: BuildState, *, expected_commit: str = "") -> dict[str, str]:
        owner = os.getenv("AUTOFORGE_GITHUB_OWNER", "").strip()
        repository = os.getenv("AUTOFORGE_GITHUB_REPOSITORY", "").strip()
        app_id = os.getenv("AUTOFORGE_GITHUB_APP_ID", "").strip()
        installation_id = os.getenv("AUTOFORGE_GITHUB_INSTALLATION_ID", "").strip()
        key_b64 = os.getenv("AUTOFORGE_GITHUB_APP_PRIVATE_KEY_BASE64", "").strip()
        if not all((owner, repository, app_id, installation_id, key_b64)):
            raise RuntimeError("GitHub publishing is not configured. Add the GitHub App settings to the backend environment.")
        if os.getenv("AUTOFORGE_GITHUB_PUBLISH_ENABLED", "false").lower() != "true":
            raise RuntimeError("GitHub publishing is disabled. Set AUTOFORGE_GITHUB_PUBLISH_ENABLED=true after configuring the GitHub App.")
        artifacts = build.proof.artifacts if build.proof else {}
        if not artifacts:
            raise RuntimeError("There are no generated artifacts to publish.")

        try:
            private_key = base64.b64decode(key_b64, validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError("AUTOFORGE_GITHUB_APP_PRIVATE_KEY_BASE64 is not valid base64-encoded PEM data.") from exc

        try:
            import jwt
        except ImportError as exc:
            raise RuntimeError("GitHub publishing requires PyJWT; install backend/requirements.txt before enabling it.") from exc
        now = int(time.time())
        app_jwt = jwt.encode({"iat": now - 30, "exp": now + 8 * 60, "iss": app_id}, private_key, algorithm="RS256")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {app_jwt}",
        }
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            token_response = await client.post(
                f"{self.api}/app/installations/{quote(installation_id, safe='')}/access_tokens",
                headers=headers,
            )
            self._raise_github(token_response, "create installation token")
            token = token_response.json().get("token")
            if not token:
                raise RuntimeError("GitHub did not return an installation token.")

            headers["Authorization"] = f"Bearer {token}"
            repo_url = f"{self.api}/repos/{quote(owner, safe='')}/{quote(repository, safe='')}"
            repo_response = await client.get(repo_url, headers=headers)
            self._raise_github(repo_response, "read repository settings")
            default_branch = os.getenv("AUTOFORGE_GITHUB_BASE_BRANCH", "").strip() or repo_response.json().get("default_branch")
            if not default_branch:
                raise RuntimeError("Could not determine the repository base branch.")
            if expected_commit:
                if not build.feature_branch or not build.feature_branch.startswith("feature/"):
                    raise RuntimeError("Deployment repair requires the original feature branch.")
                default_branch = build.feature_branch

            ref_response = await client.get(
                f"{repo_url}/git/ref/heads/{quote(default_branch, safe='/')}", headers=headers
            )
            self._raise_github(ref_response, "read base branch")
            base_sha = ref_response.json().get("object", {}).get("sha")
            if not base_sha:
                raise RuntimeError("GitHub did not return the base branch commit.")
            if expected_commit and base_sha != expected_commit:
                raise RuntimeError("Feature branch changed since the failed deployment; refusing to overwrite newer code.")

            tree_entries = []
            slug = re.sub(r"[^a-z0-9]+", "-", build.title.lower()).strip("-")[:48].strip("-") or "use-case"
            unique_id = re.sub(r"[^a-zA-Z0-9-]", "", build.id)[:24] or str(int(time.time()))
            project_root = f"generated/{slug}-{unique_id}"
            if expected_commit:
                project_root = "generated/" + build.feature_branch.removeprefix("feature/")
            for path, content in sorted(artifacts.items()):
                normalized = path.replace("\\", "/")
                if (not normalized or normalized.startswith("/") or
                    any(part in {"", ".", ".."} for part in normalized.split("/")) or
                    (len(normalized) > 1 and normalized[1] == ":")):
                    raise RuntimeError(f"Refusing to publish an unsafe artifact path: {path!r}.")
                if normalized.split("/", 1)[0].lower() in {".git", ".github"}:
                    raise RuntimeError(f"Refusing to publish repository control files: {path!r}.")
                normalized = f"{project_root}/{normalized}"
                blob_response = await client.post(
                    f"{repo_url}/git/blobs",
                    headers=headers,
                    json={"content": base64.b64encode(content.encode("utf-8")).decode("ascii"), "encoding": "base64"},
                )
                self._raise_github(blob_response, f"upload artifact {normalized}")
                tree_entries.append({"path": normalized, "mode": "100644", "type": "blob", "sha": blob_response.json()["sha"]})

            tree_response = await client.post(
                f"{repo_url}/git/trees", headers=headers,
                json={"base_tree": base_sha, "tree": tree_entries},
            )
            self._raise_github(tree_response, "create feature branch tree")
            tree_sha = tree_response.json()["sha"]
            commit_response = await client.post(
                f"{repo_url}/git/commits", headers=headers,
                # The active workflow explicitly dispatches the next run from
                # the default branch, so even old feature branches use current
                # deployment automation. Avoid a second push-triggered run.
                json={"message": f"AutoForge: {build.title[:120]}" + (" [skip ci]" if expected_commit else ""), "tree": tree_sha, "parents": [base_sha]},
            )
            self._raise_github(commit_response, "create feature branch commit")
            commit_sha = commit_response.json()["sha"]

            branch = f"feature/{slug}-{unique_id}"
            if expected_commit:
                branch = build.feature_branch
                update_ref = await client.patch(
                    f"{repo_url}/git/refs/heads/{quote(branch, safe='/')}", headers=headers,
                    json={"sha": commit_sha, "force": False},
                )
                self._raise_github(update_ref, "advance repaired feature branch")
            else:
                create_ref = await client.post(
                    f"{repo_url}/git/refs", headers=headers,
                    json={"ref": f"refs/heads/{branch}", "sha": commit_sha},
                )
                self._raise_github(create_ref, "create feature branch")

        repository_url = f"https://github.com/{owner}/{repository}"
        return {"branch": branch, "branch_url": f"{repository_url}/tree/{quote(branch, safe='/')}", "repository_url": repository_url, "commit_sha": commit_sha}

    @staticmethod
    def _raise_github(response: httpx.Response, operation: str) -> None:
        if response.is_success:
            return
        # Do not include response headers or token-bearing request details.
        try:
            detail = response.json().get("message", "")
        except ValueError:
            detail = ""
        suffix = f": {detail}" if detail else ""
        if response.status_code == 422 and operation == "create feature branch":
            suffix = ": that feature branch already exists; change the build ID or remove the existing branch."
        raise RuntimeError(f"GitHub could not {operation} (HTTP {response.status_code}){suffix}")
