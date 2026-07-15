import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


class AiGatewayError(Exception):
    """AI Gateway呼び出しをアプリケーション向けに正規化した例外。"""


class AiGatewayTimeout(AiGatewayError):
    pass


class AiGatewayUnavailable(AiGatewayError):
    pass


class AiGatewayOutputInvalid(AiGatewayError):
    pass


class SecretResolver(Protocol):
    def resolve(self, reference: str) -> str: ...


class EnvironmentSecretResolver:
    def resolve(self, reference: str) -> str:
        value = os.environ.get(reference)
        if value is None:
            normalized = reference.upper().replace("-", "_")
            value = os.environ.get(normalized)
        if not value:
            raise AiGatewayUnavailable(f"Secret参照を解決できません: {reference}")
        return value


class AiGateway(Protocol):
    def complete_json(
        self,
        *,
        base_url: str,
        api_key_secret_ref: str,
        model: str,
        messages: Sequence[Mapping[str, str]],
        timeout_seconds: int,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class OpenAiCompatibleGateway:
    secret_resolver: SecretResolver
    transport: httpx.BaseTransport | None = None

    def complete_json(
        self,
        *,
        base_url: str,
        api_key_secret_ref: str,
        model: str,
        messages: Sequence[Mapping[str, str]],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        api_key = self.secret_resolver.resolve(api_key_secret_ref)
        try:
            with httpx.Client(
                base_url=base_url.rstrip("/"),
                timeout=timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.post(
                    "/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": list(messages),
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
        except httpx.TimeoutException as error:
            raise AiGatewayTimeout("AI Gatewayがタイムアウトしました。") from error
        except httpx.HTTPError as error:
            raise AiGatewayUnavailable("AI Gatewayへ接続できません。") from error

        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise TypeError
            decoded = json.loads(content)
            if not isinstance(decoded, dict):
                raise TypeError
            return decoded
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise AiGatewayOutputInvalid("AI Gatewayの応答形式が不正です。") from error
