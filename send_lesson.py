#!/usr/bin/env python3
"""
System Design Mastery — Email Sender (File-Based)
Reads pre-generated HTML from lessons/NNN.html and sends via SMTP.
No API calls at runtime — bulletproof, fast, works offline.
"""

import os
import json
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent
TRACKER_PATH = BASE_DIR / "tracker.json"
LESSONS_DIR = BASE_DIR / "lessons"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
EMAIL_TO = os.environ["EMAIL_TO"]

TOTAL_LESSONS = 200


def load_tracker():
    with open(TRACKER_PATH) as f:
        return json.load(f)


def save_tracker(tracker):
    with open(TRACKER_PATH, "w") as f:
        json.dump(tracker, f, indent=2, default=str)


def load_lesson_meta(lesson_id):
    """Load the sidecar metadata JSON for a lesson."""
    meta_file = LESSONS_DIR / f"{lesson_id:03d}.json"
    if meta_file.exists():
        with open(meta_file) as f:
            return json.load(f)
    return {"lesson_id": lesson_id, "title": f"Lesson {lesson_id}", "system_name": "System Design", "type": "core"}


def load_lesson_html(lesson_id):
    """Load the pre-generated HTML for a lesson."""
    html_file = LESSONS_DIR / f"{lesson_id:03d}.html"
    if not html_file.exists():
        return None
    html = html_file.read_text()
    # Replace the date placeholder with today's date
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    html = html.replace("{{SEND_DATE}}", today)
    return html


def send_email(subject, html_body):
    """Send HTML email via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"System Design Daily <{SMTP_USER}>"
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    plain = f"System Design Daily — View in HTML-capable email client.\n\nSubject: {subject}"
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"[OK] Email sent: {subject}")


def main():
    print(f"\n{'='*60}")
    print(f"System Design Mastery — Lesson Sender (File-Based)")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}\n")

    tracker = load_tracker()
    current_lesson = tracker["current_lesson"]

    # Check if course is complete
    if current_lesson > TOTAL_LESSONS:
        print("[DONE] All 200 lessons have been sent! Course complete.")
        tracker["status"] = "completed"
        save_tracker(tracker)
        return

    # Load pre-generated HTML
    html_body = load_lesson_html(current_lesson)
    if html_body is None:
        error_msg = f"[ERROR] Lesson {current_lesson} HTML file not found at lessons/{current_lesson:03d}.html"
        print(error_msg)
        log_file = LOGS_DIR / f"error_{current_lesson}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file.write_text(error_msg)
        sys.exit(1)

    # Load metadata for subject line
    meta = load_lesson_meta(current_lesson)
    title = meta.get("title", f"Lesson {current_lesson}")
    system_name = meta.get("system_name", "System Design")
    lesson_type = meta.get("type", "core").upper()

    subject = f"[{lesson_type}] Lesson {current_lesson}/200: {title} — {system_name}"

    print(f"Sending lesson {current_lesson}/{TOTAL_LESSONS}:")
    print(f"  Title:  {title}")
    print(f"  System: {system_name}")
    print(f"  File:   lessons/{current_lesson:03d}.html")
    print(f"  Subject: {subject}\n")

    # Send email
    try:
        send_email(subject, html_body)
    except Exception as e:
        error_msg = f"[ERROR] Email send failed: {e}"
        print(error_msg)
        log_file = LOGS_DIR / f"error_send_{current_lesson}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file.write_text(error_msg)
        sys.exit(1)

    # Update tracker
    now_str = datetime.now(timezone.utc).isoformat()
    tracker["current_lesson"] = current_lesson + 1
    tracker["last_sent_at"] = now_str
    tracker["lessons_sent"].append({
        "lesson_id": current_lesson,
        "title": title,
        "system": system_name,
        "sent_at": now_str
    })
    if tracker["started_at"] is None:
        tracker["started_at"] = now_str
    save_tracker(tracker)

    print(f"\n{'='*60}")
    print(f"Lesson {current_lesson} sent successfully!")
    print(f"Next lesson: {current_lesson + 1}/{TOTAL_LESSONS}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
