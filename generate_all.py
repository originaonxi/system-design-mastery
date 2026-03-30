#!/usr/bin/env python3
"""
System Design Mastery — Batch Generator
Pre-generates ALL 200 lesson HTML files using Claude API.
Saves each to lessons/NNN.html. Skips already-generated lessons.
Run once, push to git, then cron just reads and sends.
"""

import os
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import anthropic

BASE_DIR = Path(__file__).parent
CURRICULUM_PATH = BASE_DIR / "curriculum.json"
TEMPLATE_PATH = BASE_DIR / "templates" / "newspaper.html"
LESSONS_DIR = BASE_DIR / "lessons"
LESSONS_DIR.mkdir(exist_ok=True)
PROGRESS_FILE = BASE_DIR / "generation_progress.json"

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TOTAL_LESSONS = 200


def load_curriculum():
    with open(CURRICULUM_PATH) as f:
        return json.load(f)


def load_template():
    with open(TEMPLATE_PATH) as f:
        return f.read()


def get_lesson_meta(curriculum, lesson_id):
    """Find lesson metadata from curriculum by lesson_id."""
    for system in curriculum["systems"]:
        for lesson in system.get("lessons", []):
            if lesson["lesson_id"] == lesson_id:
                return {
                    **lesson,
                    "system_name": system["name"],
                    "real_company": system["real_company"],
                    "system_id": system["id"],
                    "topic_in_system": system["lessons"].index(lesson) + 1,
                    "topics_in_system": len(system["lessons"])
                }

    for category, lessons in curriculum.get("bonus_lessons", {}).items():
        for i, lesson in enumerate(lessons):
            if lesson["lesson_id"] == lesson_id:
                return {
                    **lesson,
                    "system_name": category.replace("_", " ").title(),
                    "real_company": "Cross-System",
                    "system_id": 20,
                    "topic_in_system": i + 1,
                    "topics_in_system": len(lessons)
                }
    return None


def get_next_lesson_title(curriculum, lesson_id):
    """Get the title of the next lesson for the 'Coming Up Next' section."""
    next_meta = get_lesson_meta(curriculum, lesson_id + 1)
    if next_meta:
        return next_meta.get("title", "Next Lesson")
    return "Course Complete!"


def generate_lesson_content(client, lesson_meta, lesson_id, total_lessons, next_title):
    """Use Claude API to generate the full lesson content as HTML."""

    title = lesson_meta.get("title", f"Lesson {lesson_id}")
    subtitle = lesson_meta.get("subtitle", "")
    system_name = lesson_meta.get("system_name", "System Design")
    real_company = lesson_meta.get("real_company", "")
    lesson_type = lesson_meta.get("type", "core")

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
NEXT LESSON: {next_title}

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
  <p><strong>{next_title}</strong> — [One-line teaser about what they'll learn next]</p>
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


def build_email_html(template, lesson_content, lesson_meta, lesson_id, total_lessons):
    """Wrap generated content in the newspaper template."""
    progress_pct = round((lesson_id / total_lessons) * 100, 1)
    lessons_remaining = total_lessons - lesson_id

    system_name = lesson_meta.get("system_name", "System Design")
    system_id = lesson_meta.get("system_id", 0)
    topic_in_system = lesson_meta.get("topic_in_system", 1)
    topics_in_system = lesson_meta.get("topics_in_system", 1)
    lesson_type = lesson_meta.get("type", "core").upper()

    html = template.replace("{{date}}", "{{SEND_DATE}}")  # Placeholder — sender fills in actual date
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


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"generated": [], "failed": [], "last_generated": 0}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def main():
    start_from = int(sys.argv[1]) if len(sys.argv) > 1 else None

    print(f"\n{'='*70}")
    print(f"  SYSTEM DESIGN MASTERY — BATCH GENERATOR")
    print(f"  Generating all {TOTAL_LESSONS} lessons")
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*70}\n")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    curriculum = load_curriculum()
    template = load_template()
    progress = load_progress()

    # Figure out which lessons to generate
    already_done = set(progress["generated"])
    if start_from:
        to_generate = list(range(start_from, TOTAL_LESSONS + 1))
    else:
        to_generate = [i for i in range(1, TOTAL_LESSONS + 1) if i not in already_done]

    print(f"Already generated: {len(already_done)}")
    print(f"To generate: {len(to_generate)}")
    print(f"{'='*70}\n")

    success_count = 0
    fail_count = 0

    for lesson_id in to_generate:
        # Check if file already exists
        lesson_file = LESSONS_DIR / f"{lesson_id:03d}.html"
        if lesson_file.exists() and lesson_id in already_done:
            print(f"[SKIP] Lesson {lesson_id} already exists")
            continue

        lesson_meta = get_lesson_meta(curriculum, lesson_id)
        if not lesson_meta:
            lesson_meta = {
                "title": f"Lesson {lesson_id}",
                "subtitle": "System Design Deep Dive",
                "system_name": "System Design",
                "real_company": "",
                "system_id": 0,
                "topic_in_system": 1,
                "topics_in_system": 1,
                "type": "core"
            }

        title = lesson_meta.get("title", f"Lesson {lesson_id}")
        system_name = lesson_meta.get("system_name", "")
        next_title = get_next_lesson_title(curriculum, lesson_id)

        print(f"[{lesson_id:3d}/{TOTAL_LESSONS}] Generating: {title} ({system_name})")

        try:
            content = generate_lesson_content(
                client, lesson_meta, lesson_id, TOTAL_LESSONS, next_title
            )
            html = build_email_html(template, content, lesson_meta, lesson_id, TOTAL_LESSONS)

            # Save HTML file
            lesson_file.write_text(html)

            # Also save metadata sidecar for the sender
            meta_file = LESSONS_DIR / f"{lesson_id:03d}.json"
            meta_file.write_text(json.dumps({
                "lesson_id": lesson_id,
                "title": title,
                "subtitle": lesson_meta.get("subtitle", ""),
                "system_name": system_name,
                "type": lesson_meta.get("type", "core"),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "content_length": len(content)
            }, indent=2))

            progress["generated"].append(lesson_id)
            progress["last_generated"] = lesson_id
            save_progress(progress)

            success_count += 1
            print(f"         -> OK ({len(content)} chars)")

            # Rate limit: wait 2 seconds between API calls
            time.sleep(2)

        except Exception as e:
            fail_count += 1
            progress["failed"].append({"lesson_id": lesson_id, "error": str(e)})
            save_progress(progress)
            print(f"         -> FAILED: {e}")

            # On rate limit, wait longer
            if "rate" in str(e).lower():
                print("         -> Rate limited, waiting 60s...")
                time.sleep(60)
            else:
                time.sleep(5)

    print(f"\n{'='*70}")
    print(f"  GENERATION COMPLETE")
    print(f"  Success: {success_count} | Failed: {fail_count}")
    print(f"  Total in lessons/: {len(list(LESSONS_DIR.glob('*.html')))}")
    print(f"  Finished: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
