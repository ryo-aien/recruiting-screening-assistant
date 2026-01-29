import json
import logging
from typing import Any

from openai import AsyncOpenAI

from worker.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIClient:
    """Client for OpenAI API calls."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            if not self.api_key:
                raise ValueError("OpenAI API key is not configured")
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def extract_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Call OpenAI API for structured JSON extraction.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt with content to extract from
            response_format: JSON schema for response format
            model: Model to use (defaults to config)

        Returns:
            Parsed JSON response
        """
        model = model or settings.llm_model
        logger.info(f"Calling OpenAI API with model {model}")

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": 0.1,  # Low temperature for extraction
            }

            if response_format:
                kwargs["response_format"] = {"type": "json_object"}

            response = await self.client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            # Parse JSON response
            result = json.loads(content)
            logger.info("Successfully parsed OpenAI response")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    async def generate_explanation(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Generate explanation using OpenAI API.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt with context
            model: Model to use

        Returns:
            Parsed JSON explanation
        """
        return await self.extract_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
            model=model,
        )


class MockOpenAIClient(OpenAIClient):
    """Mock client for testing without API key."""

    def __init__(self):
        super().__init__(api_key="mock-key")

    async def extract_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Return mock extraction result."""
        logger.warning("Using mock OpenAI client - returning placeholder data")
        return {
            "job_requirements": {
                "must": [
                    {"id": "m1", "text": "Python experience required", "skill_tags": ["Python"]}
                ],
                "nice": [
                    {"id": "n1", "text": "AWS experience preferred", "skill_tags": ["AWS"]}
                ],
                "role_expectation": "IC",
                "year_requirements": {"Python": 3},
            },
            "candidate_profile": {
                "skills": ["Python", "JavaScript"],
                "roles": ["IC"],
                "experience_years": {"Python": 5},
                "highlights": ["5 years of Python development"],
                "concerns": [],
                "unknowns": ["AWS experience unclear"],
            },
            "evidence": {
                "job": {"must:m1": "Python experience required"},
                "candidate": {"skill:Python": "5 years of Python development"},
            },
        }

    async def generate_explanation(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Return mock explanation result."""
        logger.warning("Using mock OpenAI client - returning placeholder explanation")
        return {
            "summary": "Strong Python candidate with relevant experience.",
            "strengths": ["5 years Python experience", "Good technical background"],
            "concerns": ["AWS experience unclear"],
            "unknowns": ["Team collaboration style"],
            "must_gaps": [],
        }


def get_openai_client() -> OpenAIClient:
    """Get OpenAI client, falling back to mock if no API key."""
    if settings.openai_api_key:
        return OpenAIClient()
    logger.warning("No OpenAI API key configured, using mock client")
    return MockOpenAIClient()
