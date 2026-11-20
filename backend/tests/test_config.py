from app.core.config import Settings


def test_default_settings(monkeypatch):
    monkeypatch.delenv("OLLAMA_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.ollama_url == "http://localhost:11434/api/generate"
    assert settings.ollama_model == "qwen2.5:3b-instruct"


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://test-server:11434/api/generate")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model:1b")

    settings = Settings(_env_file=None)

    assert settings.ollama_url == "http://test-server:11434/api/generate"
    assert settings.ollama_model == "test-model:1b"
