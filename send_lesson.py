#!/usr/bin/env python3
"""
System Design Mastery — AI-Powered Email Lesson Sender
Generates ultra-detailed system design lessons using Claude API
and sends them as newspaper-format HTML emails every 3 hours.
"""

import os
import json
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from pathlib import Path
import anthropic

# ── Config ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
TRACKER_PATH = BASE_DIR / "tracker.json"
CURRICULUM_PATH = BASE_DIR / "curriculum.json"
TEMPLATE_PATH = BASE_DIR / "templates" / "newspaper.html"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
EMAIL_TO = os.environ["EMAIL_TO"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]


def load_tracker():
    with open(TRACKER_PATH) as f:
        return json.load(f)


def save_tracker(tracker):
    with open(TRACKER_PATH, "w") as f:
        json.dump(tracker, f, indent=2, default=str)


def load_curriculum():
    with open(CURRICULUM_PATH) as f:
        return json.load(f)


def get_lesson_meta(curriculum, lesson_id):
    """Find lesson metadata from curriculum by lesson_id."""
    # Search in main systems
    for system in curriculum["systems"]:
        for lesson in system.get("lessons", []):
            if lesson["lesson_id"] == lesson_id:
                return {**lesson, "system_name": system["name"], "real_company": system["real_company"],
                        "system_id": system["id"],
                        "topic_in_system": system["lessons"].index(lesson) + 1,
                        "topics_in_system": len(system["lessons"])}

    # Search in bonus lessons
    for category, lessons in curriculum.get("bonus_lessons", {}).items():
        for lesson in lessons:
            if lesson["lesson_id"] == lesson_id:
                return {**lesson, "system_name": category.replace("_", " ").title(),
                        "real_company": "Cross-System",
                        "system_id": 20, "topic_in_system": 1,
                        "topics_in_system": len(lessons)}

    return None


def find_system_for_lesson(curriculum, lesson_id):
    """Get system number for a lesson."""
    for system in curriculum["systems"]:
        for lesson in system.get("lessons", []):
            if lesson["lesson_id"] == lesson_id:
                return system["id"]
    return 0


def generate_lesson_content(lesson_meta, lesson_id, total_lessons):
    """Use Claude API to generate the full lesson content as HTML."""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    title = lesson_meta.get("title", f"Lesson {lesson_id}")
    subtitle = lesson_meta.get("subtitle", "")
    system_name = lesson_meta.get("system_name", "System Design")
    real_company = lesson_meta.get("real_company", "")
    lesson_type = lesson_meta.get("type", "core")

    # Build context from structured data if available
    context_parts = []
    if "real_numbers" in lesson_meta:
        context_parts.append(f"Key metrics: {json.dumps(lesson_meta['real_numbers'])}")
    if "real_obstacle" in lesson_meta:
        context_parts.append(f"Real obstacle to cover: {lesson_meta['real_obstacle']}")
    if "papers" in lesson_meta:
        context_parts.append(f"Papers/sources to reference: {json.dumps(lesson_meta['papers'])}")
    if "napkin_math" in lesson_meta:
        context_parts.append(f"Napkin math to include: {lesson_meta['napkin_math']}")
    if "ai_smb_angle" in lesson_meta:
        context_parts.append(f"AI for SMBs angle: {lesson_meta['ai_smb_angle']}")
    if "interview_questions" in lesson_meta:
        context_parts.append(f"Interview questions: {json.dumps(lesson_meta['interview_questions'])}")
    if "topics" in lesson_meta:
        context_parts.append(f"Must cover these topics: {json.dumps(lesson_meta['topics'])}")

    extra_context = "\n".join(context_parts) if context_parts else "Generate comprehensive coverage of this topic."

    prompt = f"""You are writing a detailed system design lesson for an advanced software engineer who wants to become world-class. This is lesson {lesson_id} of {total_lessons} in a comprehensive system design mastery course.

LESSON: {title}
SUBTITLE: {subtitle}
SYSTEM: {system_name} ({real_company})
TYPE: {lesson_type}

CONTEXT AND DATA:
{extra_context}

Generate the COMPLETE lesson content as HTML fragments (no <html>, <head>, or <body> tags — just the inner content divs). The content MUST be extremely detailed (2500-3500 words), factual, with real numbers, real papers, and real engineering decisions.

You MUST include ALL of these sections using EXACTLY these HTML structures:

1. HEADLINE & INTRO:
<h2 class="headline">{title}</h2>
<p class="subtitle">{subtitle}</p>
<p class="body-text">Opening paragraph that hooks with a surprising fact or number...</p>

2. ARCHITECTURE DIAGRAM (ASCII art in a diagram box):
<div class="section-header">Architecture</div>
<div class="diagram-box">
[Create a detailed ASCII architecture diagram showing the key components and data flow. Make it at least 15 lines. Use boxes ┌─┐│└─┘, arrows →←↑↓, and labels. This should be a REAL architecture diagram someone could whiteboard in an interview.]
</div>
<p class="body-text">Explanation of the diagram...</p>

3. HOW IT WORKS (Deep technical breakdown - this should be the longest section):
<div class="section-header">How It Works — Deep Dive</div>
<p class="body-text">Detailed explanation with multiple paragraphs...</p>
[Include at least 4-5 detailed paragraphs with technical depth. Explain protocols, data structures, algorithms, and engineering tradeoffs. Reference specific technologies and version numbers where applicable.]

4. BY THE NUMBERS (Use number cards):
<div class="section-header">By The Numbers</div>
<div class="numbers-grid">
  <div class="number-card"><div class="value">VALUE</div><div class="label">LABEL</div></div>
  [Include 4-6 number cards with real, factual metrics]
</div>

5. REAL OBSTACLE / WAR STORY:
<div class="obstacle-box">
  <div class="label">Real Obstacle — What Actually Went Wrong</div>
  <p>[Detailed real-world failure story with dates, companies, dollar amounts, and root cause. This must be a REAL incident, not made up. Include the timeline, what broke, impact, and how it was fixed.]</p>
</div>

6. NAPKIN MATH:
<div class="napkin-math">
  <div class="label">Napkin Math — Back of Envelope</div>
  <p>[Show step-by-step calculations an interviewer would expect. Start from basic assumptions, multiply through, and arrive at infrastructure requirements. Show your work.]</p>
</div>

7. TRADE-OFF TABLE:
<div class="section-header">Engineering Trade-Offs</div>
<table class="tradeoff-table">
  <tr><th>Decision</th><th>Option A</th><th>Option B</th><th>What They Chose</th><th>Why</th></tr>
  [Include 3-4 real engineering decisions with honest tradeoffs]
</table>

8. CODE SNIPPET (Real, runnable Python):
<div class="section-header">Code — Key Algorithm</div>
<div class="code-block">
[Write a real, working Python implementation of the KEY algorithm or data structure for this lesson. 20-40 lines. Include comments. This should be something they can run and learn from.]
</div>
<p class="body-text">Explanation of the code...</p>

9. SCALE PROGRESSION:
<div class="section-header">Scale Progression</div>
<div class="scale-progression">
  <div class="scale-step"><div class="scale-dot" style="background:#4caf50"></div><strong>1K users:</strong>&nbsp; [What the architecture looks like]</div>
  <div class="scale-step"><div class="scale-dot" style="background:#ff9800"></div><strong>1M users:</strong>&nbsp; [What changes]</div>
  <div class="scale-step"><div class="scale-dot" style="background:#f44336"></div><strong>1B users:</strong>&nbsp; [What the final architecture looks like]</div>
</div>

10. AI FOR SMBs (How to rebuild this with AI):
<div class="ai-smb-box">
  <div class="label">AI-First SMB Version — Build This Today</div>
  <p>[How an SMB would build a simplified version of this system using modern AI tools: Claude API, vector databases, serverless, managed services. Be specific — name exact tools, APIs, estimated costs. Include a mini-architecture showing the AI-enhanced version.]</p>
</div>

11. PULL QUOTE:
<div class="pull-quote">"[A memorable, insightful quote about this system or concept — either from a real engineer or a synthesized insight]"</div>

12. SOURCES & PAPERS:
<div class="section-header">Sources & Further Reading</div>
<p>
[Include 6-10 source links using this format:]
<a class="source-link" href="URL">Paper/Article Title — Source</a>
[Include: original papers, engineering blog posts, conference talks, official documentation. These must be REAL URLs to real resources.]
</p>

13. INTERVIEW CORNER:
<div class="interview-box">
  <div class="label">Interview Corner — FAANG-Level Questions</div>
  <ol>
    <li><strong>Q:</strong> [Interview question]<br><strong>Model Answer:</strong> [2-3 sentence answer hitting the key points an interviewer wants to hear]</li>
    [Include 3 questions with model answers]
  </ol>
</div>

14. NEXT UP PREVIEW:
<div class="next-up">
  <div class="label">Coming Up Next</div>
  <p><strong>[Next lesson title]</strong> — [One-line teaser about what they'll learn]</p>
</div>

CRITICAL RULES:
- Every number must be REAL and factual (cite source if needed)
- Every outage/incident must be REAL with correct dates
- Papers and links must point to REAL resources
- Code must actually WORK if someone runs it
- ASCII diagrams must be detailed enough to whiteboard
- Write for someone targeting Staff/Principal Engineer level
- No fluff, no padding — every sentence must teach something
- Include the AI for SMBs section showing how to rebuild with modern AI tools
- Be specific: name technologies, version numbers, team sizes, dates"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def build_email_html(lesson_content, lesson_meta, lesson_id, total_lessons):
    """Wrap generated content in the newspaper template."""

    with open(TEMPLATE_PATH) as f:
        template = f.read()

    now = datetime.now(timezone.utc)
    progress_pct = round((lesson_id / total_lessons) * 100, 1)
    lessons_remaining = total_lessons - lesson_id

    system_name = lesson_meta.get("system_name", "System Design")
    system_id = lesson_meta.get("system_id", 0)
    topic_in_system = lesson_meta.get("topic_in_system", 1)
    topics_in_system = lesson_meta.get("topics_in_system", 1)
    lesson_type = lesson_meta.get("type", "core").upper()

    html = template.replace("{{date}}", now.strftime("%B %d, %Y"))
    html = html.replace("{{lesson_number}}", str(lesson_id))
    html = html.replace("{{total_lessons}}", str(total_lessons))
    html = html.replace("{{lesson_type}}", lesson_type)
    html = html.replace("{{progress_pct}}", str(progress_pct))
    html = html.replace("{{lessons_remaining}}", str(lessons_remaining))
    html = html.replace("{{system_number}}", str(system_id))
    html = html.replace("{{system_name}}", system_name)
    html = html.replace("{{topic_in_system}}", str(topic_in_system))
    html = html.replace("{{topics_in_system}}", str(topics_in_system))
    html = html.replace("{{content}}", lesson_content)

    return html


def send_email(subject, html_body):
    """Send HTML email via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"System Design Daily <{SMTP_USER}>"
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    # Plain text fallback
    plain = f"System Design Daily — View in HTML-capable email client.\n\nSubject: {subject}"
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"[OK] Email sent: {subject}")


def main():
    """Main entry point — generate and send next lesson."""
    print(f"\n{'='*60}")
    print(f"System Design Mastery — Lesson Sender")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}\n")

    # Load state
    tracker = load_tracker()
    curriculum = load_curriculum()

    current_lesson = tracker["current_lesson"]
    total_lessons = tracker["total_lessons"]

    # Check if course is complete
    if current_lesson > total_lessons:
        print("[DONE] All 200 lessons have been sent! Course complete.")
        tracker["status"] = "completed"
        save_tracker(tracker)
        return

    # Get lesson metadata
    lesson_meta = get_lesson_meta(curriculum, current_lesson)
    if not lesson_meta:
        print(f"[WARN] No metadata for lesson {current_lesson}, creating generic entry")
        lesson_meta = {
            "title": f"Lesson {current_lesson}",
            "subtitle": "System Design Deep Dive",
            "system_name": "System Design",
            "real_company": "",
            "system_id": 0,
            "topic_in_system": 1,
            "topics_in_system": 1,
            "type": "core"
        }

    title = lesson_meta.get("title", f"Lesson {current_lesson}")
    subtitle = lesson_meta.get("subtitle", "")
    system_name = lesson_meta.get("system_name", "")

    print(f"Generating lesson {current_lesson}/{total_lessons}:")
    print(f"  System: {system_name}")
    print(f"  Title:  {title}")
    print(f"  Subtitle: {subtitle}\n")

    # Generate content via Claude API
    print("Calling Claude API to generate lesson content...")
    try:
        lesson_content = generate_lesson_content(lesson_meta, current_lesson, total_lessons)
        print(f"  Content generated: {len(lesson_content)} chars\n")
    except Exception as e:
        error_msg = f"[ERROR] Claude API failed: {e}"
        print(error_msg)
        # Log error
        log_file = LOGS_DIR / f"error_{current_lesson}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file.write_text(error_msg)
        sys.exit(1)

    # Build HTML email
    html_body = build_email_html(lesson_content, lesson_meta, current_lesson, total_lessons)

    # Compose subject line
    lesson_type_label = lesson_meta.get("type", "core").upper()
    subject = f"[{lesson_type_label}] Lesson {current_lesson}/200: {title} — {system_name}"

    # Send email
    print(f"Sending email: {subject}")
    try:
        send_email(subject, html_body)
    except Exception as e:
        error_msg = f"[ERROR] Email send failed: {e}"
        print(error_msg)
        log_file = LOGS_DIR / f"error_send_{current_lesson}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file.write_text(error_msg)
        sys.exit(1)

    # Save generated content to lessons/ directory
    lesson_file = BASE_DIR / "lessons" / f"{current_lesson:03d}_{title.lower().replace(' ', '_').replace('/', '_')[:50]}.html"
    lesson_file.write_text(html_body)
    print(f"  Saved to: {lesson_file.name}")

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
    print(f"Next lesson: {current_lesson + 1}/{total_lessons}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
