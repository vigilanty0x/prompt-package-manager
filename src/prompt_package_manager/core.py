from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any

PROJECT = "prompt-package-manager"
REQUIRED_FIELDS = ["name","version","prompt","variables","output_schema","tests"]

def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_text(item) for item in value)

def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)

def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def build_prompt_package(record: dict[str, Any]) -> dict[str, Any]:
    if not _text(record["name"]) or not isinstance(record["version"], str) or not re.fullmatch(r"\d+\.\d+\.\d+", record["version"]):
        raise ValueError("name and semantic version are required")
    if not _text(record["prompt"]) or not _string_list(record["variables"]) or len(record["variables"]) != len(set(record["variables"])):
        raise ValueError("prompt variables must be unique non-empty strings")
    placeholders = set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", record["prompt"]))
    if placeholders != set(record["variables"]):
        raise ValueError("declared variables must match prompt placeholders")
    if not isinstance(record["output_schema"], dict) or not record["output_schema"] or not isinstance(record["tests"], list) or not record["tests"] or any(not isinstance(test, dict) or not test for test in record["tests"]):
        raise ValueError("output schema and tests are required")
    payload = {key: record[key] for key in ("name", "version", "prompt", "variables", "output_schema", "tests")}
    return {"name": record["name"], "version": record["version"], "digest": sha256(_canonical(payload).encode()).hexdigest(), "test_count": len(record["tests"])}

def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    artifact: Any = None
    if missing:
        status = "blocked"
        reason = "missing required fields: " + ", ".join(missing)
    else:
        try:
            artifact = build_prompt_package(record)
            status = "passed"
            reason = "build_prompt_package completed"
        except (TypeError, ValueError, KeyError) as exc:
            status = "failed"
            reason = str(exc)
    receipt = {"project": PROJECT, "status": status, "reason": reason, "record": record, "package_manifest": artifact}
    receipt["evidence_sha256"] = sha256(_canonical(receipt).encode()).hexdigest()
    return receipt

