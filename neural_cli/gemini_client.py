"""
Gemini Client Module - Neural Architect Integration.

Ce module fournit un client configuré pour Google Gemini/Vertex AI
avec le persona "Neural Architect" du projet CyberIDE.

Version: 1.0.0
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Generator

from pydantic import BaseModel, Field, field_validator


class SafetySettings(BaseModel):
    """Configuration des paramètres de sécurité Gemini."""

    hate_speech: str = Field(default="OFF", alias="HARM_CATEGORY_HATE_SPEECH")
    dangerous_content: str = Field(default="OFF", alias="HARM_CATEGORY_DANGEROUS_CONTENT")
    sexually_explicit: str = Field(default="OFF", alias="HARM_CATEGORY_SEXUALLY_EXPLICIT")
    harassment: str = Field(default="OFF", alias="HARM_CATEGORY_HARASSMENT")


class GenerationConfig(BaseModel):
    """Configuration de génération pour Gemini."""

    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    max_output_tokens: int = Field(default=65535, gt=0)
    safety_settings: SafetySettings = Field(default_factory=SafetySettings)


class ModelConfig(BaseModel):
    """Configuration du modèle Gemini."""

    default_model: str = Field(default="gemini-3-pro-preview")
    thinking_budget: str = Field(default="auto")
    thinking_level: str = Field(default="HIGH")

    @field_validator("thinking_level")
    @classmethod
    def validate_thinking_level(cls, v: str) -> str:
        allowed = {"LOW", "MEDIUM", "HIGH"}
        if v.upper() not in allowed:
            msg = f"thinking_level must be one of {allowed}"
            raise ValueError(msg)
        return v.upper()


class GeminiSettings(BaseModel):
    """Configuration complète Gemini chargée depuis settings.json."""

    model: ModelConfig = Field(default_factory=ModelConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)

    @classmethod
    def from_settings_file(cls, settings_path: Path | None = None) -> GeminiSettings:
        """Charge la configuration depuis .gemini/settings.json."""
        if settings_path is None:
            # Cherche le fichier settings.json dans le projet
            project_root = Path(__file__).parent.parent
            settings_path = project_root / ".gemini" / "settings.json"

        if not settings_path.exists():
            # Configuration par défaut si pas de fichier
            return cls()

        with settings_path.open() as f:
            data = json.load(f)

        return cls(
            model=ModelConfig(
                default_model=data.get("model", {}).get("defaultModel", "gemini-3-pro-preview"),
                thinking_budget=data.get("model", {}).get("thinkingBudget", "auto"),
                thinking_level=data.get("model", {}).get("thinkingLevel", "HIGH"),
            ),
            generation=GenerationConfig(
                temperature=data.get("generation", {}).get("temperature", 1.0),
                top_p=data.get("generation", {}).get("topP", 0.95),
                max_output_tokens=data.get("generation", {}).get("maxOutputTokens", 65535),
                safety_settings=SafetySettings(
                    **data.get("generation", {}).get("safetySettings", {})
                ),
            ),
        )


def load_system_prompt(prompt_name: str = "neural-architect") -> str:
    """
    Charge le system prompt depuis le fichier versionné.

    Args:
        prompt_name: Nom du fichier prompt (sans extension)

    Returns:
        Contenu du system prompt
    """
    project_root = Path(__file__).parent.parent
    prompt_path = project_root / ".gemini" / "prompts" / f"{prompt_name}.md"

    if not prompt_path.exists():
        msg = f"System prompt not found: {prompt_path}"
        raise FileNotFoundError(msg)

    content = prompt_path.read_text(encoding="utf-8")

    # Retire le header markdown (metadata) pour ne garder que le prompt
    lines = content.split("\n")
    in_header = False
    prompt_lines: list[str] = []

    for line in lines:
        if line.strip() == "---":
            in_header = not in_header
            continue
        if not in_header and not line.startswith("#"):
            prompt_lines.append(line)

    return "\n".join(prompt_lines).strip()


class NeuralArchitectClient:
    """
    Client Gemini configuré avec le persona Neural Architect.

    Usage:
        client = NeuralArchitectClient()
        for chunk in client.generate("Ajoute une route pour lister les users"):
            print(chunk, end="")
    """

    def __init__(
        self,
        api_key: str | None = None,
        use_vertex: bool = True,
        settings: GeminiSettings | None = None,
    ) -> None:
        """
        Initialise le client Gemini.

        Args:
            api_key: Clé API (défaut: GOOGLE_CLOUD_API_KEY env var)
            use_vertex: Utiliser Vertex AI (True) ou Gemini API directe (False)
            settings: Configuration personnalisée (défaut: charge depuis settings.json)
        """
        # Import tardif pour éviter erreur si package non installé
        try:
            from google import genai
            from google.genai import types
        except ImportError as e:
            msg = "google-cloud-aiplatform not installed. Run: uv add google-cloud-aiplatform"
            raise ImportError(msg) from e

        self._genai = genai
        self._types = types

        self.api_key = api_key or os.environ.get("GOOGLE_CLOUD_API_KEY")
        self.use_vertex = use_vertex
        self.settings = settings or GeminiSettings.from_settings_file()
        self.system_prompt = load_system_prompt()

        # Initialise le client
        self._client = genai.Client(
            vertexai=self.use_vertex,
            api_key=self.api_key,
        )

    def _build_config(self) -> "types.GenerateContentConfig":
        """Construit la configuration de génération."""
        types = self._types

        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ]

        return types.GenerateContentConfig(
            temperature=self.settings.generation.temperature,
            top_p=self.settings.generation.top_p,
            max_output_tokens=self.settings.generation.max_output_tokens,
            safety_settings=safety_settings,
            system_instruction=[types.Part.from_text(text=self.system_prompt)],
            thinking_config=types.ThinkingConfig(
                thinking_level=self.settings.model.thinking_level,
            ),
        )

    def generate(self, user_message: str) -> Generator[str, None, None]:
        """
        Génère une réponse en streaming.

        Args:
            user_message: Message de l'utilisateur

        Yields:
            Chunks de texte de la réponse
        """
        types = self._types

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)],
            )
        ]

        config = self._build_config()

        for chunk in self._client.models.generate_content_stream(
            model=self.settings.model.default_model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                yield chunk.text

    def generate_sync(self, user_message: str) -> str:
        """
        Génère une réponse complète (non-streaming).

        Args:
            user_message: Message de l'utilisateur

        Returns:
            Réponse complète
        """
        return "".join(self.generate(user_message))


# Fonction de compatibilité avec le snippet original
def generate(user_message: str = "") -> None:
    """
    Fonction de compatibilité avec le snippet original.

    Usage:
        from neural_cli.gemini_client import generate
        generate("Ajoute une route pour lister les utilisateurs")
    """
    client = NeuralArchitectClient()
    for chunk in client.generate(user_message):
        print(chunk, end="")
    print()  # Newline final


if __name__ == "__main__":
    # Test rapide
    import sys

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = "Quel est l'etat de sante du Neural Core?"

    generate(message)
