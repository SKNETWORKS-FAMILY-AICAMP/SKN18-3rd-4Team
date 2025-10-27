import os


def set_openapi() -> str | None:
    """Return the OpenAI API key from the environment."""
    return os.getenv("OPENAI_API_KEY")

