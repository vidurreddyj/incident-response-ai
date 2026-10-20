import json
from unittest.mock import Mock, patch
from sample_data import sample_incident, sample_commits
from pipeline import process_incident
from reports import estimate_impact
from github import recent_commits
from analysis import analyze


def test_impact():
    assert estimate_impact(sample_incident()["metrics"])["excess_failed_requests"] == 1400


def test_pipeline_offline(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = process_incident(sample_incident())
    assert result["diagnosis"]["mode"] == "offline"
    assert result["commit_source"] == "sample"
    assert "blocks" in result["slack"]
    assert "post-incident report" in result["postmortem"].lower()


def test_github_api(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    item = {"sha": "abc123", "commit": {"message": "Fix bug", "committer": {"date": "2026-10-18T12:00:00Z"}}}
    with patch("github.requests.get") as get:
        get.side_effect = [Mock(json=Mock(return_value=[item])),
                           Mock(json=Mock(return_value={"files": [{"filename": "app.py", "status": "modified", "patch": "+fix"}]}))]
        commits = recent_commits("test", "repo", limit=1)
    assert commits[0]["files"][0]["name"] == "app.py"
    assert get.call_count == 2


def test_gemini_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    body = {"root_cause": "Likely null handling regression", "recommendation": "Inspect diff",
            "ranked_commits": [{"sha": "a1b2c3", "confidence": 0.8, "reason": "Matches logs"},
                               {"sha": "invalid", "confidence": 1, "reason": "Not supplied"}]}
    with patch("analysis.requests.post") as post:
        post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]}
        result = analyze(sample_incident(), sample_commits())
    assert result["mode"] == "gemini"
    assert len(result["ranked_commits"]) == 1
    assert result["ranked_commits"][0]["sha"] == "a1b2c3"
