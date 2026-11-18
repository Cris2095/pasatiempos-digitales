"""Ask a model through the local FCC proxy (Anthropic-compatible) and save the reply.

Usage:
    python fcc_ask.py --model anthropic/groq/openai/gpt-oss-120b --prompt-file prompt.txt --out reply.md

Reads the prompt from a file and passes it as a single argv element internally
(HTTP body here, so no shell expansion is involved).
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

TOKEN_FILE = Path(r"C:\AgentSharedMemory\runtime-workspace\fcc-home\.fcc\.token")
PROXY = "http://127.0.0.1:8082"


def token() -> str:
    try:
        value = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if value:
            return value
    except OSError:
        pass
    return "freecc"


def ask(model: str, prompt: str, max_tokens: int = 4000, timeout: int = 600) -> str:
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    request = urllib.request.Request(
        PROXY + "/v1/messages?beta=true",
        data=body,
        headers={
            "Authorization": "Bearer " + token(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    parts = []
    for block in payload.get("content") or []:
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
    if not parts:
        raise RuntimeError("empty content: " + json.dumps(payload)[:400])
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-tokens", type=int, default=4000)
    args = parser.parse_args()
    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    try:
        answer = ask(args.model, prompt, args.max_tokens)
    except (urllib.error.URLError, RuntimeError, TimeoutError) as exc:
        print("FCC_ERROR: " + type(exc).__name__ + ": " + str(exc)[:300], file=sys.stderr)
        return 2
    Path(args.out).write_text(answer, encoding="utf-8")
    print("OK bytes=" + str(len(answer.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
