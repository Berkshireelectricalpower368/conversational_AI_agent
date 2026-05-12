"""
Date utility functions for the Google Drive File Discovery Assistant.

Provides helpers to compute relative date strings (e.g., "last week",
"this month") in RFC 3339 format, which Google Drive API requires for
modifiedTime queries.
"""

from datetime import datetime, timedelta, timezone


def get_current_datetime() -> datetime:
    """Get the current UTC datetime."""
    return datetime.now(timezone.utc)


def to_rfc3339(dt: datetime) -> str:
    """
    Convert a datetime to RFC 3339 format string.
    
    This is the format Google Drive API expects for date comparisons.
    Example output: '2026-05-11T00:00:00Z'
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_relative_dates() -> dict:
    """
    Compute commonly-used relative date boundaries in RFC 3339 format.
    
    Returns a dictionary with date strings that can be injected into
    the AI system prompt, so the LLM knows the actual dates for
    queries like "last week" or "this month".
    
    Returns:
        Dict with keys like 'today', 'yesterday', 'start_of_this_week', etc.
    """
    now = get_current_datetime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    return {
        "now":                  to_rfc3339(now),
        "today":                to_rfc3339(today_start),
        "yesterday":            to_rfc3339(today_start - timedelta(days=1)),
        "start_of_this_week":   to_rfc3339(today_start - timedelta(days=today_start.weekday())),
        "start_of_last_week":   to_rfc3339(today_start - timedelta(days=today_start.weekday() + 7)),
        "end_of_last_week":     to_rfc3339(today_start - timedelta(days=today_start.weekday())),
        "start_of_this_month":  to_rfc3339(today_start.replace(day=1)),
        "start_of_last_month":  to_rfc3339(
            (today_start.replace(day=1) - timedelta(days=1)).replace(day=1)
        ),
        "end_of_last_month":    to_rfc3339(today_start.replace(day=1) - timedelta(days=1)),
        "last_7_days":          to_rfc3339(today_start - timedelta(days=7)),
        "last_14_days":         to_rfc3339(today_start - timedelta(days=14)),
        "last_30_days":         to_rfc3339(today_start - timedelta(days=30)),
        "last_90_days":         to_rfc3339(today_start - timedelta(days=90)),
        "start_of_this_year":   to_rfc3339(today_start.replace(month=1, day=1)),
    }


def format_dates_for_prompt() -> str:
    """
    Generate a formatted string of current date references for the
    AI system prompt. This gives the LLM concrete dates to use when
    the user says things like "this week" or "last month".
    """
    dates = get_relative_dates()
    return f"""Current Date/Time Reference (UTC):
  - Right now:           {dates['now']}
  - Today starts at:     {dates['today']}
  - Yesterday:           {dates['yesterday']}
  - This week started:   {dates['start_of_this_week']}
  - Last week:           {dates['start_of_last_week']} to {dates['end_of_last_week']}
  - This month started:  {dates['start_of_this_month']}
  - Last month:          {dates['start_of_last_month']} to {dates['end_of_last_month']}
  - Last 7 days:         {dates['last_7_days']}
  - Last 30 days:        {dates['last_30_days']}
  - This year started:   {dates['start_of_this_year']}"""
