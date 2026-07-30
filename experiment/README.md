# oTree experiment

This directory contains the participant-facing oTree program used for the bachelor's thesis experiment. The interface and most instructions are in Simplified Chinese.

## Experimental sequence

The active sequence is defined in `settings.py`:

1. `instruction`
2. `manager_y1`
3. `svo_investor`
4. `investor_y1`
5. `manager_y2`
6. `investor_y2`
7. `manager_y3`
8. `investor_y3`
9. `svo_manager`
10. `questionnaire`

The three manager-investor rounds use different industry report materials. Managers choose disclosure complexity through a strategy-method interface. Investors either read independently or use the embedded FinGPT-style chat assistant before giving an ESG score, confidence judgment, and comprehension answers.

The existing Chinese [`experiment audit and variable guide`](./docs/experiment_audit_and_variable_guide.md) provides a detailed field map and payoff summary.

## Local setup

The historical environment used:

- Python with oTree 5.11.1
- CNY experimental currency
- an OpenAI-compatible third-party endpoint for the AI assistant
- a Gemini 3.1 Flash-Lite preview model alias

Create an isolated environment, install the dependencies, set the required environment variables, and then use the standard oTree development command:

```shell
python -m venv .venv
python -m pip install -r requirements.txt
otree devserver
```

At minimum, set `OTREE_ADMIN_PASSWORD` and `OTREE_SECRET_KEY` for any deployment. The AI-assisted pages also require your own `BIANXIE_API_KEY`. The repository root contains an [environment-variable template](../.env.example), but the program does not automatically load `.env` files.

## Security and privacy changes in this public copy

The research working directory contained runtime and machine-specific files that do not belong in a public repository. This copy excludes:

- the local SQLite database and its WAL/SHM files;
- Conda and IDE directories;
- Python bytecode and caches;
- an oTree backup archive;
- an unrelated local utility script; and
- a hard-coded API credential.

The three investor apps now read the API credential only from `BIANXIE_API_KEY`. The original credential should be treated as compromised and rotated before the working copy is used again.

The room-label list has been renamed to `jointhegame.example.txt` to make clear that it contains demonstration labels rather than participant data.

## Reproduction limits

- The AI endpoint and model alias may change or disappear.
- Exact model responses are not deterministic and may differ from those observed during data collection.
- Participant-level data and analysis scripts are not included.
- Pre-generated calibration and ESG report PDFs are retained because the experiment interfaces depend on them.
- Public availability does not grant a license for unrestricted reuse.

This is therefore an inspectable experiment archive, not yet a turnkey replication package.
