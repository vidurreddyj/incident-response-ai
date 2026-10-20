"""
main.py

Allows users to manually enter incident information through the terminal
and investigate the incident using real GitHub commits and Gemini.

The program collects incident details, passes them to the investigation
pipeline, and saves the generated reports in the outputs folder.
"""
import json
from pathlib import Path
from pipeline import process_incident


def ask(prompt):
    """
    Repeatedly asks the user for input until a nonempty response is entered.

    Args:
        prompt (str): Question displayed to the user in the terminal.

    Returns:
        str: The user's response with surrounding whitespace removed.
    """
    while True:
        answer = input(prompt).strip()
        if answer:
            return answer
        print("Please enter a value.")


def ask_number(prompt, minimum=0, maximum=None):
    """
    Asks the user for a number and checks whether it is within the
    allowed range. Repeats the question if the input is invalid.

    Args:
        prompt (str): Question displayed to the user.
        minimum (float): Smallest allowed value (default is 0).
        maximum (float or None): Largest allowed value, or None for no limit.

    Returns:
        float: A valid number entered by the user.
    """
    while True:
        try:
            value = float(ask(prompt))
            if value < minimum or (maximum is not None and value > maximum):
                raise ValueError
            return value
        except ValueError:
            print("Please enter a valid number in the requested range.")


def collect_incident():
    """
    Collects incident information manually entered by the user.

    Asks for the affected service, severity, error logs, deployment
    details, and performance metrics. This information is organized
    into a dictionary that the pipeline uses to investigate the incident.

    Returns:
        dict: Incident information containing service details, error logs,
              deployment information, and performance metrics.
    """
    print("\nEnter incident information:")
    service = ask("Service name: ")
    severity = ask("Severity (e.g. high): ")
    print("Enter log lines, then press Enter on an empty line to finish:")
    logs = []

    # Collects multiple error logs until the user enters an empty line.
    while True:
        line = input("Log: ").strip()
        if line:
            logs.append(line)
        elif logs:
            break
        else:
            print("At least one log line is required.")

    version = ask("Deployment version (or 'unknown'): ")
    deployed_at = ask("Deployment time (UTC ISO 8601, or 'unknown'): ")

    print("\nEnter metrics for the same observation period:")

    # Collects metrics used to estimate the incident's impact.
    # Error rates are decimals between 0 and 1 (e.g., 0.15 = 15%).
    requests = int(ask_number("Total requests: "))
    baseline = ask_number("Normal error rate (0-1): ", maximum=1)
    current = ask_number("Current error rate (0-1): ", maximum=1)
    per_user = ask_number("Requests per user (>0): ", minimum=0.000001)
    order_value = ask_number("Average order value ($, use 0 if not applicable): ")

    # Organizes the collected information into the format
    # expected by process_incident() in pipeline.py.
    return {
        "service": service, "severity": severity, "logs": logs,
        "deployment": {"version": version, "deployed_at": deployed_at},
        "metrics": {"requests": requests, "baseline_error_rate": baseline,
                    "current_error_rate": current, "requests_per_user": per_user,
                    "average_order_value": order_value},
    }


def save_reports(result):
    """
    Saves the investigation results and generated reports to the outputs folder.

    Creates the folder if it does not exist, then saves the incident
    investigation, Slack-formatted message, and postmortem report.

    Args:
        result (dict): Investigation results returned by process_incident().

    Returns:
        None: Saves the three report files without returning a value.
    """
    out = Path("outputs")

    # Creates the outputs folder if it does not already exist.
    out.mkdir(exist_ok=True)

    # Creates a dictionary excluding Slack and postmortem reports,
    # since those are saved separately.
    evidence = {k: v for k, v in result.items() if k not in ("slack", "postmortem")}

    # json.dumps() converts Python dictionaries into formatted JSON strings.
    # indent=2 makes the JSON easier to read.
    (out / "incident.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (out / "slack.json").write_text(json.dumps(result["slack"], indent=2), encoding="utf-8")
    # Saves the postmortem as a Markdown file.
    (out / "postmortem.md").write_text(result["postmortem"], encoding="utf-8")


def main():
    """
    Runs the incident response program from the terminal.

    Collects the GitHub repository information and incident details,
    calls the investigation pipeline to analyze real GitHub commits,
    and saves the generated reports.

    Returns:
        None: Displays the suspected root cause and saves the reports.
    """
    print("Incident Response AI - Manual Incident Entry")

    # Identifies the GitHub repository to investigate.
    owner = ask("GitHub repository owner: ")
    repo = ask("GitHub repository name: ")

    # Collects the incident details entered by the user.
    incident = collect_incident()
    print("\nFetching real GitHub commits and analyzing the incident...")

    # Runs the investigation pipeline.
    # use_github=True requests real commits instead of sample commits.
    result = process_incident(incident, owner=owner, repo=repo, use_github=True)

    # Saves the investigation results to the outputs folder.
    save_reports(result)

    # Displays the analysis method and suspected root cause.
    print("Analysis mode:", result["diagnosis"]["mode"])
    print("Suspected cause:", result["diagnosis"]["root_cause"])
    print("Reports saved to outputs/")

# Runs main() only when this file is executed directly.
# It will not run automatically if main.py is imported by another file.
if __name__ == "__main__":
    main()
