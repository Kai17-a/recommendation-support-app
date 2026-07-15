import base64
import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

ISSUER = "http://mock-services:8080"
KEY_ID = "integration-key"
API_KEY = "integration-secret"
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_NUMBERS = PRIVATE_KEY.public_key().public_numbers()

app = FastAPI(title="OIDC and OpenAI-compatible integration mock")


def _encoded_number(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/.well-known/openid-configuration")
async def discovery() -> dict[str, str]:
    return {"issuer": ISSUER, "jwks_uri": f"{ISSUER}/jwks"}


@app.get("/jwks")
async def jwks() -> dict[str, list[dict[str, str]]]:
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": KEY_ID,
                "n": _encoded_number(PUBLIC_NUMBERS.n),
                "e": _encoded_number(PUBLIC_NUMBERS.e),
            }
        ]
    }


@app.post("/token")
async def token(subject: str = Query(...)) -> dict[str, str]:
    now = datetime.now(UTC)
    access_token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": "recommendation-support-api",
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=10),
        },
        PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": KEY_ID},
    )
    return {"access_token": access_token, "token_type": "Bearer"}


class ChatRequest(BaseModel):
    model: str
    messages: list[dict[str, str]]


@app.post("/v1/chat/completions")
async def chat_completion(
    command: ChatRequest, authorization: str | None = Header(default=None)
) -> dict[str, Any]:
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="invalid API key")
    if command.model == "failure-model":
        raise HTTPException(status_code=503, detail="intentional integration failure")

    system = command.messages[0]["content"]
    user = command.messages[-1]["content"]
    snapshot = _snapshot(user)
    if "fact_summary" in system:
        project_id = snapshot["project"]["id"]
        output = {
            "fact_summary": ["案件経験の事実を確認しました。"],
            "skill_candidates": [],
            "strength_candidates": [],
            "evidence": [
                {
                    "source_type": "project_experience",
                    "source_id": project_id,
                    "quote_or_summary": snapshot["project"]["project_name"],
                }
            ],
            "missing_information": [],
        }
    elif '"draft"' in system:
        project = snapshot["projects"][0]
        output = {
            "draft": [
                {
                    "paragraph_no": 1,
                    "text": "案件で確認された経験に基づく推薦文ドラフトです。",
                    "evidence": [
                        {
                            "source_type": "project_experience",
                            "source_id": project["id"],
                            "quote_or_summary": project["project_name"],
                        }
                    ],
                }
            ],
            "warnings": [],
        }
    else:
        output = {"ambiguities": [], "evidence_map": {}}

    return {
        "id": "mock-completion",
        "object": "chat.completion",
        "choices": [{"message": {"role": "assistant", "content": json.dumps(output)}}],
    }


def _snapshot(content: str) -> dict[str, Any]:
    found = re.search(r"<data>\n(.*)\n</data>", content, flags=re.DOTALL)
    return json.loads(found.group(1)) if found else {}
