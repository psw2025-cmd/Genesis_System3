"""
Dashboard Continuous Improvement System
Analyzes issues, identifies improvements, and implements fixes
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytz

sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
ISSUES_LOG = Path(__file__).parent.parent / "logs" / "dashboard_issues.log"
IMPROVEMENTS_LOG = Path(__file__).parent.parent / "logs" / "dashboard_improvements.log"
ANALYSIS_FILE = Path(__file__).parent.parent / "outputs" / "dashboard_improvement_analysis.json"


def analyze_issues():
    """Analyze logged issues to identify patterns"""
    if not ISSUES_LOG.exists():
        return {}

    try:
        with open(ISSUES_LOG, "r", encoding="utf-8") as f:
            issues = json.load(f)
    except:
        return {}

    # Analyze last 24 hours
    cutoff = datetime.now(IST) - timedelta(hours=24)

    recent_issues = [issue for issue in issues if datetime.fromisoformat(issue["timestamp"].replace(" ", "T")) > cutoff]

    # Group by type
    issue_counts = {}
    unresolved = []

    for issue in recent_issues:
        issue_type = issue.get("type", "unknown")
        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        if not issue.get("resolved", False):
            unresolved.append(issue)

    # Identify patterns
    patterns = {}
    for issue_type, count in issue_counts.items():
        if count >= 3:  # Recurring issue
            patterns[issue_type] = {
                "count": count,
                "frequency": "high" if count >= 10 else "medium",
                "recommendation": get_recommendation(issue_type),
            }

    return {
        "total_issues_24h": len(recent_issues),
        "unresolved_count": len(unresolved),
        "issue_counts": issue_counts,
        "patterns": patterns,
        "top_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5],
    }


def get_recommendation(issue_type):
    """Get improvement recommendation for issue type"""
    recommendations = {
        "backend_down": "Implement automatic backend restart with exponential backoff. Add health check endpoint monitoring.",
        "frontend_down": "Implement automatic frontend restart. Add process monitoring.",
        "api_endpoints_failed": "Add endpoint health monitoring. Implement circuit breaker pattern.",
        "backend_restart_failed": "Check system resources. Verify Python environment. Add detailed error logging.",
        "frontend_restart_failed": "Check Node.js installation. Verify npm dependencies. Add dependency verification.",
        "connection_timeout": "Increase timeout values. Optimize API response times. Add connection pooling.",
        "data_consistency": "Implement data validation. Add consistency checks. Monitor data sources.",
        "market_transition": "Improve market detection logic. Add transition event logging. Verify synthetic data generation.",
    }

    return recommendations.get(issue_type, "Monitor and investigate root cause.")


def generate_improvements():
    """Generate improvement suggestions based on analysis"""
    analysis = analyze_issues()

    improvements = []

    # High-frequency issues
    if analysis.get("patterns"):
        for issue_type, pattern in analysis["patterns"].items():
            if pattern["frequency"] == "high":
                improvements.append(
                    {
                        "priority": "high",
                        "type": "fix_recurring_issue",
                        "issue_type": issue_type,
                        "description": f"Fix recurring issue: {issue_type} (occurred {pattern['count']} times)",
                        "recommendation": pattern["recommendation"],
                        "estimated_impact": "high",
                    }
                )

    # Unresolved issues
    if analysis.get("unresolved_count", 0) > 0:
        improvements.append(
            {
                "priority": "medium",
                "type": "resolve_unresolved",
                "description": f"Resolve {analysis['unresolved_count']} unresolved issues",
                "recommendation": "Review unresolved issues log and implement fixes",
                "estimated_impact": "medium",
            }
        )

    # Performance improvements
    if analysis.get("total_issues_24h", 0) > 50:
        improvements.append(
            {
                "priority": "medium",
                "type": "performance_optimization",
                "description": "High issue count suggests performance optimization needed",
                "recommendation": "Review system performance. Optimize API endpoints. Add caching.",
                "estimated_impact": "high",
            }
        )

    return improvements


def save_analysis(analysis, improvements):
    """Save analysis and improvements"""
    data = {
        "timestamp": datetime.now(IST).isoformat(),
        "analysis": analysis,
        "improvements": improvements,
        "next_review": (datetime.now(IST) + timedelta(hours=1)).isoformat(),
    }

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    return data


def main():
    """Run improvement analysis"""
    print("=" * 60)
    print("DASHBOARD CONTINUOUS IMPROVEMENT ANALYSIS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    analysis = analyze_issues()
    improvements = generate_improvements()

    print("ISSUE ANALYSIS (Last 24 Hours):")
    print(f"  Total Issues: {analysis.get('total_issues_24h', 0)}")
    print(f"  Unresolved: {analysis.get('unresolved_count', 0)}")
    print()

    if analysis.get("top_issues"):
        print("TOP ISSUES:")
        for issue_type, count in analysis["top_issues"]:
            print(f"  {issue_type}: {count} occurrences")
        print()

    if improvements:
        print("IMPROVEMENTS RECOMMENDED:")
        for i, improvement in enumerate(improvements, 1):
            print(f"  {i}. [{improvement['priority'].upper()}] {improvement['description']}")
            print(f"     Recommendation: {improvement['recommendation']}")
        print()
    else:
        print("No improvements recommended at this time.")
        print()

    # Save analysis
    data = save_analysis(analysis, improvements)

    print(f"Analysis saved to: {ANALYSIS_FILE}")
    print()

    return data


if __name__ == "__main__":
    main()
