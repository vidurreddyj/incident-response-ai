"""
pipeline.py

Connects incident information, GitHub commits, Gemini analysis, and reports.

Retrieves real GitHub commits or sample commits, sends the evidence to
Gemini for root cause analysis, estimates incident impact, and generates
Slack summaries and postmortem reports.
"""

from analysis import analyze
from github import recent_commits
from reports import estimate_impact, runbook, slack_summary, postmortem
from sample_data import sample_commits


def process_incident(incident, owner=None, repo=None, use_github=False):
    """
    Processes an incident and generates investigation results.

    Retrieves commits from GitHub or sample data, analyzes the incident
    using Gemini, estimates its impact, and generates incident reports.

    Args:
        incident (dict): Incident details including logs, deployment, and metrics.
        owner (str or None): GitHub repository owner.
        repo (str or None): GitHub repository name.
        use_github (bool): Whether to retrieve real GitHub commits.
                           Defaults to False for sample commits.

    Returns:
        dict: Complete investigation results containing incident details,
              commits, Gemini diagnosis, impact estimates, runbook,
              Slack summary, and postmortem report.
    """

    # Retrieves real GitHub commits when requested.
    if use_github:
        if not owner or not repo:
            raise ValueError("GitHub owner and repo are required")

        commits = recent_commits(owner, repo)
        source = f"github:{owner}/{repo}"

    else:
        # Uses simulated commits for testing or demonstrations.
        commits = sample_commits()
        source = "sample"

    # Sends the incident information and commits to Gemini for analysis and gets an answer(diagnosis)
    diagnosis = analyze(incident, commits)

    # Combines the original incident with the investigation results.
    # **incident copies all existing incident dictionary entries.
    result = {
        **incident,
        "commit_source": source,
        "commits": commits,
        "diagnosis": diagnosis,
        "impact": estimate_impact(incident["metrics"]),
        "runbook": runbook(incident["service"])
    }

    # Generates a Slack-formatted incident summary.
    result["slack"] = slack_summary(result)

    # Generates a postmortem report using the investigation results.
    result["postmortem"] = postmortem(result)

    return result

