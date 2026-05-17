import base64
import json
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from auth import get_google_creds


# ── Gmail helpers ──────────────────────────────────────────────────────────────

def list_emails(query: str = "", max_results: int = 10) -> str:
    service = build("gmail", "v1", credentials=get_google_creds())
    result = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = result.get("messages", [])
    if not messages:
        return "No emails found."

    items = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        snippet = detail.get("snippet", "")[:100]
        items.append(
            f"ID: {msg['id']}\n"
            f"From: {headers.get('From', 'unknown')}\n"
            f"Subject: {headers.get('Subject', '(no subject)')}\n"
            f"Snippet: {snippet}"
        )
    return "\n\n".join(items)


def send_email(to: str, subject: str, body: str) -> str:
    service = build("gmail", "v1", credentials=get_google_creds())
    mime = MIMEText(body)
    mime["to"] = to
    mime["subject"] = subject
    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return f"Email sent to {to}."


# ── Calendar helpers ───────────────────────────────────────────────────────────

def list_events(time_min: str, time_max: str) -> str:
    service = build("calendar", "v3", credentials=get_google_creds())
    result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = result.get("items", [])
    if not events:
        return "No events found in that range."

    items = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        items.append(f"- {start}: {e.get('summary', '(no title)')}")
    return "\n".join(items)


def create_event(summary: str, start: str, end: str, description: str = "") -> str:
    service = build("calendar", "v3", credentials=get_google_creds())
    body = {
        "summary": summary,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }
    if description:
        body["description"] = description
    event = service.events().insert(calendarId="primary", body=body).execute()
    return f"Event created: {event.get('htmlLink', 'link unavailable')}"


# ── Tool schemas (passed to Claude) ───────────────────────────────────────────

TOOLS = [
    {
        "name": "list_emails",
        "description": "Search Gmail and return sender, subject, snippet, and message ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Gmail search query, e.g. 'from:boss'"},
                "max_results": {"type": "integer", "description": "Max emails to return (default 10)"},
            },
            "required": [],
        },
    },
    {
        "name": "send_email",
        "description": "Send an email via Gmail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "list_events",
        "description": "List Google Calendar events between two ISO 8601 datetimes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "time_min": {"type": "string", "description": "Start of range, e.g. 2025-05-01T00:00:00Z"},
                "time_max": {"type": "string", "description": "End of range, e.g. 2025-05-31T23:59:59Z"},
            },
            "required": ["time_min", "time_max"],
        },
    },
    {
        "name": "create_event",
        "description": "Create a Google Calendar event.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Event title"},
                "start": {"type": "string", "description": "ISO 8601 start datetime"},
                "end": {"type": "string", "description": "ISO 8601 end datetime"},
                "description": {"type": "string", "description": "Optional event description"},
            },
            "required": ["summary", "start", "end"],
        },
    },
]


# ── Dispatcher ────────────────────────────────────────────────────────────────

def run_tool(name: str, input: dict) -> str:
    if name == "list_emails":
        return list_emails(**input)
    if name == "send_email":
        return send_email(**input)
    if name == "list_events":
        return list_events(**input)
    if name == "create_event":
        return create_event(**input)
    raise ValueError(f"Unknown tool: {name}")
