# Incident Response AI — Manual Entry

Investigate manually supplied production errors using **real GitHub commits** and **Google Gemini**. No FastAPI, Datadog, or monitoring service is needed.

## How it works

`main.py` asks for a GitHub repository, error logs, deployment details, and metrics. `github.py` fetches recent commits and diffs from that repository. `analysis.py` asks Gemini to rank suspected commits (or uses an offline keyword heuristic if no Gemini key is provided). `reports.py` estimates impact, loads local troubleshooting runbooks, and generates report content.

## Setup (PowerShell)

```powershell
python -m pip install -r requirements.txt
$env:GEMINI_API_KEY="YOUR_GEMINI_KEY"
python main.py
```

Get a Gemini key at https://aistudio.google.com/apikey. The default model is `gemini-2.5-flash`; set `$env:GEMINI_MODEL` to a model supported by your account if necessary.

For public repositories, GitHub authentication is optional. For private repositories or higher API rate limits, set `$env:GITHUB_TOKEN="YOUR_GITHUB_TOKEN"` using a token with appropriate read permissions. Do not commit keys or tokens. Run the command in the project folder.

## Manual input

Enter the repository owner and name, service, severity, one or more real log lines, deployment version/time (enter `unknown` if unavailable), total requests, normal/current error rates as decimals between 0 and 1, requests per user, and average order value. The numeric metrics are required for the existing impact calculations. Use `0` for average order value if not relevant. **Do not fabricate real incident metrics.** Estimates are meaningful only when the inputs are meaningful.

## Output

- `outputs/incident.json` — incident, commits, AI diagnosis, impact, runbook
- `outputs/slack.json` — Slack-compatible message (not sent automatically)
- `outputs/postmortem.md` — draft postmortem (not verified)

## Other commands

```powershell
python demo.py          # Existing simulated demo (does not need manual input)
python -m pytest -q  # Run unit tests
```

## Limitations

This tool does not detect incidents. It does not verify which commits were deployed or prove causation. It examines only recent GitHub commits, so relevant commits might be missed. Gemini confidence scores are subjective. If `GEMINI_API_KEY` is missing, the system uses an offline keyword-matching fallback. The revenue-at-risk estimate is a simplified calculation, not verified financial loss. Reports are drafts for human review.
