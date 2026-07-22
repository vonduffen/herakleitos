"""Pluggable judge/model backends.

Any OpenAI-compatible or Anthropic-compatible chat endpoint can serve as a
judge or as a candidate model. Configuration lives in ``evals/judge/config.toml``
and never hard-codes a provider: swap judges by editing config, per the plan's
requirement that the frontier grader be swappable.

Frontier backends are for OFFLINE GRADING ONLY (see MODELS.md). Nothing
returned by a frontier backend may be written into training data.
"""

from __future__ import annotations

import json
import os
import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx

CONFIG_PATH = Path(__file__).resolve().parent / "config.toml"


class Backend(Protocol):
    name: str

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str: ...


@dataclass
class OpenAICompatBackend:
    name: str
    base_url: str
    model: str
    api_key_env: str
    temperature: float = 0.0

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        key = os.environ.get(self.api_key_env, "")
        if not key:
            raise RuntimeError(f"backend {self.name}: set {self.api_key_env}")
        resp = httpx.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


@dataclass
class AnthropicBackend:
    name: str
    model: str
    api_key_env: str = "ANTHROPIC_API_KEY"
    base_url: str = "https://api.anthropic.com"
    temperature: float = 0.0

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        key = os.environ.get(self.api_key_env, "")
        if not key:
            raise RuntimeError(f"backend {self.name}: set {self.api_key_env}")
        resp = httpx.post(
            f"{self.base_url.rstrip('/')}/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": self.temperature,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]


def _default_mock_reply(system: str, user: str) -> str:
    """Well-formed (but content-free) JSON for each rubric, keyed off the system
    prompt. Lets the calibrate/report CLIs run fully offline as a wiring smoke.
    """
    # Key off a phrase unique to each rubric's system prompt. Order matters
    # only as a fallback; the anchors are chosen to be mutually exclusive.
    s = system.lower()
    if "classify its provenance" in s:
        return json.dumps({"label": "genuine", "confidence": 0.5, "rationale": "mock"})
    if "applies heraclitean structure" in s:
        seg = user[user.find("Binary checks:") : user.find("Response:")]
        n = max(1, len(re.findall(r"(?m)^\d+\.", seg)))
        return json.dumps({"checks": [True] * n, "score": 3, "rationale": "mock"})
    if "anti-kitsch detector" in s:
        return json.dumps({"flags": [], "score": 3, "rationale": "mock"})
    if "holds a genuine both-and" in s:
        return json.dumps(
            {"collapse_turn": None, "collapse_mode": "none", "score": 3, "rationale": "mock"}
        )
    if "two responses of purportedly equal insight" in s:
        return json.dumps({"winner": "B", "rationale": "mock"})
    if "check statements against the core commitments" in s:
        return json.dumps({"label": "compatible", "violated_commitment": None, "rationale": "mock"})
    return json.dumps({"score": 3, "rationale": "mock"})


@dataclass
class MockBackend:
    """Deterministic backend for tests and smoke evals. No network."""

    name: str = "mock"
    responder: Callable[[str, str], str] | None = None

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        if self.responder is not None:
            return self.responder(system, user)
        return _default_mock_reply(system, user)


def load_backend(name: str, config_path: Path = CONFIG_PATH) -> Backend:
    cfg = tomllib.loads(config_path.read_text())
    try:
        b = cfg["backends"][name]
    except KeyError as e:
        raise KeyError(f"backend {name!r} not in {config_path}") from e
    kind = b.get("kind", "openai")
    if kind == "anthropic":
        return AnthropicBackend(
            name=name,
            model=b["model"],
            api_key_env=b.get("api_key_env", "ANTHROPIC_API_KEY"),
            base_url=b.get("base_url", "https://api.anthropic.com"),
        )
    if kind == "openai":
        return OpenAICompatBackend(
            name=name,
            base_url=b["base_url"],
            model=b["model"],
            api_key_env=b.get("api_key_env", "OPENAI_API_KEY"),
        )
    if kind == "mock":
        return MockBackend(name=name)
    raise ValueError(f"unknown backend kind {kind!r}")
