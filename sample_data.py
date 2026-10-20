
"""
sample_data.py

Provides simulated incident information and GitHub commits for testing
the incident response system without a real production failure.

Contains:
- sample_incident(): Returns simulated error logs, deployment details, and metrics.
- sample_commits(): Returns simulated GitHub commits for root cause analysis.
"""


def sample_incident():
    """
    Creates a simulated incident involving a checkout service.

    Provides error logs, deployment information, and service metrics
    that the system uses to investigate the failure and estimate its impact.

    Returns:
        dict: Incident details including the service, severity, logs,
              deployment information, and performance metrics.
    """
    return {
        "service": "checkout-api",
        "severity": "high",

        # The application tried to access 'token' on a None value.
        # HTTP 500 indicates an internal server error.
        "logs": ["AttributeError: 'NoneType' object has no attribute 'token'",
                 "POST /checkout returned HTTP 500"],

        # The version deployed and its deployment time (UTC).
        "deployment": {"version": "v2.4.1", "deployed_at": "2026-10-18T12:00:00Z"},

        # Metrics used to estimate failed requests, affected users, and revenue impact.
        "metrics": {
            "requests": 10000,             # Total requests
            "baseline_error_rate": 0.01,   # Normal error rate (1%)
            "current_error_rate": 0.15,    # Current error rate (15%)
            "requests_per_user": 3,        # Average requests per user
            "average_order_value": 45      # Average order value in dollars
        },
    }


def sample_commits():
    """
    Creates simulated GitHub commits that may be related to the incident.

    Each commit includes its identifier, message, timestamp, and modified
    files. The system analyzes these changes to identify possible causes
    of the error.

    Returns:
        list: A list of commit dictionaries containing the SHA, message,
              date, and modified files with their code patches.
    """
    return [
        {
            # SHA is a unique identifier for a Git commit.
            "sha": "a1b2c3",
            "message": "Remove null check from payment token validation",
            "date": "2026-10-18T11:55:00Z",

            "files": [
                {
                    "name": "payment.py",

                    # '-' indicates removed code. Removing this check
                    # could cause the NoneType error in the incident.
                    "patch": "-if token is None: return error"
                }
            ]
        },

        {
            "sha": "d4e5f6",
            "message": "Update checkout button styling",
            "date": "2026-10-18T11:40:00Z",

            "files": [
                {
                    "name": "styles.css",

                    # '+' indicates added code. This styling change
                    # is unlikely to cause the checkout error.
                    "patch": "+color: blue"
                }
            ]
        },
    ]
