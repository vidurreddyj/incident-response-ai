"""
demo.py

Demonstrates the incident response system using sample incident data.

Runs the investigation pipeline with sample commits by default,
or real GitHub commits when enabled, and saves the generated reports.
"""

import json
import os
from pathlib import Path
from pipeline import process_incident
from sample_data import sample_incident


def main():
    """
    Runs a demonstration of the incident response system.

    Loads sample incident data, runs the investigation pipeline,
    saves the generated reports, and displays the suspected root cause.

    Returns:
        None: Saves the reports and displays the investigation results.
    """

    # Use real GitHub commits if USE_GITHUB is set to "1".
    # Otherwise, use sample commits.
    use_github = os.getenv("USE_GITHUB") == "1"

    # Send sample incident data and GitHub settings to pipeline.py.
    result = process_incident(
        sample_incident(),
        os.getenv("GITHUB_OWNER"),
        os.getenv("GITHUB_REPO"),
        use_github
    )

    # Create the outputs folder if it does not exist.
    out = Path("outputs")
    out.mkdir(exist_ok=True)

    # Save incident details and investigation results as JSON.
    # Slack and postmortem are excluded because they are saved separately.
    (out / "incident.json").write_text(
        json.dumps(
            {k: v for k, v in result.items()
             if k not in ("slack", "postmortem")},
            indent=2
        ),
        encoding="utf-8"
    )

    # Save the Slack-formatted incident summary.
    (out / "slack.json").write_text(
        json.dumps(result["slack"], indent=2),
        encoding="utf-8"
    )

    # Save the postmortem report as a Markdown file.
    (out / "postmortem.md").write_text(
        result["postmortem"],
        encoding="utf-8"
    )

    # Display the investigation summary.
    print(f"Service: {result['service']} | commits: {result['commit_source']} | AI mode: {result['diagnosis']['mode']}")
    print("Suspected cause:", result["diagnosis"]["root_cause"])
    print("Reports saved to outputs/")


# Run main() only when demo.py is executed directly.
if __name__ == "__main__":
    main()

