"""
LLM client abstraction for the AI-Resume-Analyzer-Career-Coach-Agent backend.

This module defines a thin wrapper around the actual Large Language Model (LLM)
provider. The wrapper is intentionally minimal and currently contains only
placeholder logic so that the system architecture can be developed and tested
without requiring a real model or network access.

Clean Architecture Considerations:
- Agents and controllers should depend only on this abstraction, not directly
  on a particular SDK (e.g., OpenAI, Anthropic, etc.).
- This decoupling makes it easier to:
    - Swap providers.
    - Mock the LLM in unit tests.
    - Add cross-cutting concerns (logging, tracing, caching, rate limiting).
"""

import os
from typing import Any


class OpenAIClient:
    """
    Simple client wrapper for future OpenAI (or similar) API integration.

    IMPORTANT:
    - This class does NOT make real API calls yet.
    - All interactions are represented as placeholders to keep the system
      runnable without external dependencies.
    """

    def __init__(self) -> None:
        # In a real implementation, this is where you would:
        # - Read API keys.
        # - Configure model names and defaults.
        # - Set up any HTTP session clients or retry logic.
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def generate_response(self, prompt: str) -> Any:
        """
        Generate a response for a given prompt using an LLM.

        Parameters
        ----------
        prompt:
            A fully constructed prompt string that encodes the task for the
            language model. Typically built using templates from `utils.prompts`.

        Returns
        -------
        Any
            In a real implementation, this would likely be a dict or structured
            object parsed from the model's JSON/text response. For now, we
            return a static placeholder payload so that the rest of the code
            can be executed without external services.
        """
        # TODO: Call LLM here using structured prompt.
        # Example (pseudocode):
        #   client = openai.OpenAI(api_key=self.api_key)
        #   response = client.chat.completions.create(
        #       model="gpt-4.1",
        #       messages=[{"role": "user", "content": prompt}],
        #   )
        #   return response

        # Placeholder response structure. Agents are currently not relying
        # on this output; instead they use deterministic stand-ins. Once
        # real LLM integration is added, this method will become the primary
        # bridge between agent prompts and model outputs.
        return {
            "mock": True,
            "prompt_echo": prompt[:200],  # limit size to keep logs reasonable
            "message": "LLM integration is not yet implemented.",
        }


__all__ = ["OpenAIClient"]

