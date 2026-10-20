"""
reports.py

Estimates incident impact, retrieves runbooks, and generates
Slack summaries and postmortem reports.
"""

from pathlib import Path


def estimate_impact(metrics):
    """
    Estimates the impact of an incident using service metrics.

    Args:
        metrics (dict): Request counts, error rates, and revenue information.

    Returns:
        dict: Estimated excess failed requests, affected users,
              and potential revenue at risk.
    """

    # Calculate additional failed requests compared to the baseline.
    excess = max(0, round(metrics["requests"] * (metrics["current_error_rate"] - metrics["baseline_error_rate"])))

    # Estimate affected users based on requests per user.
    users = round(excess / max(1, metrics.get("requests_per_user", 1)))

    # Estimate potential revenue at risk.
    revenue = round(excess * metrics.get("average_order_value", 0), 2)

    return {"excess_failed_requests": excess, "estimated_affected_users": users,
            "potential_revenue_at_risk": revenue}


def runbook(service):
    """
    Retrieves troubleshooting instructions for the affected service.

    Args:
        service (str): Name of the affected service.

    Returns:
        str: Contents of the relevant runbook file.
    """

    # Locate the runbooks folder.
    folder = Path(__file__).resolve().parent / "runbooks"

    # Select the checkout runbook or the general runbook.
    name = "checkout.md" if "checkout" in service else "general.md"

    return (folder / name).read_text(encoding="utf-8")


def slack_summary(result):
    """
    Creates a Slack-formatted summary of the incident.

    Args:
        result (dict): Incident details, diagnosis, and impact estimates.

    Returns:
        dict: Slack message containing incident severity, diagnosis,
              estimated impact, and recommended action.
    """

    diagnosis = result["diagnosis"]
    impact = result["impact"]

    # Build a Slack message using the incident results.
    return {"blocks": [
        {"type": "header", "text": {"type": "plain_text", "text": f"Incident: {result['service']}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text":
         f"*Severity:* {result['severity']}\n*Diagnosis:* {diagnosis['root_cause']}\n"
         f"*Estimated excess failures:* {impact['excess_failed_requests']}\n"
         f"*Potential revenue at risk:* ${impact['potential_revenue_at_risk']:,.2f}\n"
         f"*Recommendation:* {diagnosis['recommendation']}"}},
    ]}


def postmortem(result):
    """
    Generates a draft post-incident report in Markdown format.

    Args:
        result (dict): Incident details, Gemini diagnosis, and impact estimates.

    Returns:
        str: Markdown report containing the incident summary,
             candidate commits, impact, and suggested resolution.
    """

    d, i = result["diagnosis"], result["impact"]

    # Format ranked commits with confidence scores and reasons.
    ranked = "\n".join(f"- `{x['sha']}`: {x['confidence']:.0%} — {x['reason']}" for x in d["ranked_commits"])

    # Generate the postmortem report.
    return (f"# Post-incident report (draft) — {result['service']}\n\n"
            f"## Summary\n{d['root_cause']}\n\n## Deployment\n{result['deployment']}\n\n"
            f"## Candidate commits\n{ranked or 'None'}\n\n"
            f"## Impact (estimates)\nExcess failures: {i['excess_failed_requests']}\n"
            f"Affected users: {i['estimated_affected_users']}\n"
            f"Potential revenue at risk: ${i['potential_revenue_at_risk']:,.2f}\n\n"
            f"## Suggested resolution\n{d['recommendation']}\n\n"
            "## Follow-up\nVerify deployed SHA and error-rate recovery; add regression tests.\n\n"
            "_Draft based on supplied incident data; requires human review._\n")

