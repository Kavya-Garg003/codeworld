"""LLM provider abstraction: none (offline/extractive), ollama (local, CPU ok), openai-compatible (Groq, Gemini, OpenRouter, LM Studio, llama.cpp ...)."""
from __future__ import annotations
import httpx


class LLM:
    name = "none"
    available = False

    def chat(self, messages: list[dict], temperature: float = 0.1, max_tokens: int = 900) -> str:
        raise RuntimeError("no LLM configured")


class NullLLM(LLM):
    pass


class OllamaLLM(LLM):
    available = True

    def __init__(self, model: str, base: str):
        self.model, self.base, self.name = model, base.rstrip("/"), f"ollama:{model}"

    def chat(self, messages, temperature=0.1, max_tokens=900):
        r = httpx.post(f"{self.base}/api/chat", timeout=300, json={
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens, "num_ctx": 8192}})
        r.raise_for_status()
        return r.json()["message"]["content"]


class OpenAICompatLLM(LLM):
    available = True

    def __init__(self, model: str, base: str, key: str):
        self.model, self.base, self.key, self.name = model, base.rstrip("/"), key, f"openai:{model}"

    def chat(self, messages, temperature=0.1, max_tokens=900):
        r = httpx.post(f"{self.base}/chat/completions", timeout=180,
                       headers={"Authorization": f"Bearer {self.key}"} if self.key else {},
                       json={"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def get_llm(settings) -> LLM:
    p = settings.llm_provider
    if p == "ollama":
        return OllamaLLM(settings.llm_model, settings.llm_base_url)
    if p in ("openai", "openai-compatible", "groq", "gemini", "openrouter"):
        return OpenAICompatLLM(settings.llm_model, settings.llm_base_url, settings.llm_api_key)
    return NullLLM()
