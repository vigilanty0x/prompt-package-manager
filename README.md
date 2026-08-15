# Prompt Package Manager

Version prompts, variables, output schemas, tests, and changelogs.

## Quick start

```bash
python -m pip install -e .
prompt-package-manager examples/valid.json
```

The command emits deterministic fail-closed JSON and a SHA-256 evidence identifier. It uses synthetic input and has zero runtime dependencies.

## Verify

```bash
python -m unittest discover -s tests -v
python scripts/check.py
```

Apache-2.0. Python 3.11+.

