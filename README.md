# System Design Mastery — 200 Lessons Straight to Your Inbox

**Learn how the world's biggest systems actually work — one email every 3 hours.**

19 real-world system design case studies. 200 deep-dive lessons. Pre-generated HTML newspaper-format emails delivered automatically via cron. No fluff — real architecture diagrams, real outage post-mortems, real numbers, real code.

---

## What You'll Learn

| # | System | Company | Lessons |
|---|--------|---------|---------|
| 1 | Stock Exchange | NASDAQ / NYSE | Order matching, order book, market data, circuit breakers, settlement, co-location, fault tolerance |
| 2 | Payment System | Stripe / Square | Payment flow, PCI-DSS, idempotency, fraud detection ML, multi-currency, ledger, 5-nines reliability |
| 3 | YouTube | Google | Video upload pipeline, CDN, recommendations, Vitess, live streaming, content moderation, ad auction |
| 4 | Google Docs | Google Workspace | OT vs CRDT, WebSockets, revision history, conflict resolution, offline sync, permissions |
| 5 | Apache Kafka | Confluent / LinkedIn | Brokers/topics/partitions, log storage, exactly-once, Kafka Streams, replication, 7T messages/day |
| 6 | Pastebin | Pastebin | URL shortening, rate limiting, storage tiering, CDN caching, TTL expiration |
| 7 | WhatsApp | Meta | E2E encryption, Erlang/BEAM, delivery guarantees, media pipeline, group messaging, presence |
| 8 | Airbnb | Airbnb | Search ranking, dynamic pricing, payment escrow, trust & safety, geo-spatial search (S2) |
| 9 | Spotify | Spotify | Audio streaming, Discover Weekly, 800+ microservices, P2P→CDN pivot, A/B testing, podcasts |
| 10 | Slack | Salesforce | WebSocket gateway, channel architecture, search 100B+ messages, notifications, Slack Connect |
| 11 | Reddit | Reddit | Ranking algorithms, vote counting, Python→Go migration, comment trees, AutoModerator |
| 12 | Google Search | Google | Web crawling, PageRank, query processing, ranking evolution, Knowledge Graph, ads auction |
| 13 | Real-Time Leaderboard | Gaming | Redis ZSET, sharded leaderboards, time-windowed, approximate ranking, anti-cheat |
| 14 | Twitter Timeline | X | Fan-out strategies, Snowflake IDs, materialized timelines, celebrity problem, trends detection |
| 15 | Uber ETA | Uber | Graph routing, real-time traffic, ETA ML model, dispatch, surge pricing, H3 hex grid |
| 16 | Amazon Lambda | AWS | Cold starts, Firecracker microVM, event-driven, concurrency, Lambda@Edge, Step Functions |
| 17 | Amazon S3 | AWS | 11-nines durability, storage classes, consistent hashing, replication, S3 Select |
| 18 | Apple AirTags | Apple | BLE beacons, Find My mesh network, privacy architecture, UWB, anti-stalking |
| 19 | ChatGPT / LLMs | OpenAI | Transformers, training infra, RLHF, inference optimization, tool use, safety |

### Bonus Content (Lessons 128–200)

- **15 Cross-System Pattern Maps** — Consistent hashing, fan-out, caching, rate limiting, sharding, ML in production
- **13 Comparison Deep Dives** — WhatsApp vs Slack, Kafka vs RabbitMQ, SQL vs NoSQL, REST vs GraphQL vs gRPC
- **15 Capstone Challenges** — Design TikTok, Robinhood, Discord, Notion, DoorDash, Netflix, Coinbase, Figma, Copilot
- **15 AI-for-SMBs Deep Dives** — Rebuild these systems with AI: fraud detection, vector search, RAG, AI agents
- **5 Scale Progressions** — 0 → 1K → 100K → 1M → 100M → 1B users
- **5 Real Outage Post-Mortems** — AWS S3, Facebook, Slack, YouTube, Cloudflare
- **5 Interview Masterclass** — Framework, napkin math, CAP theorem, NFRs, final exam

---

## What Each Email Looks Like

Every lesson is a full **newspaper-format HTML email** with:

- **Architecture Diagram** — ASCII art you can whiteboard in interviews
- **Deep Dive** — 2500–3500 words of technical breakdown with real protocols, algorithms, data structures
- **By The Numbers** — Real factual metrics from the actual companies
- **Real Obstacle** — Actual outage or failure with dates, dollar amounts, root cause analysis
- **Napkin Math** — Step-by-step back-of-envelope calculations
- **Trade-Off Table** — Real engineering decisions with pros/cons and what they chose
- **Code Snippet** — Runnable Python implementing the key algorithm
- **Scale Progression** — How architecture changes from 1K → 1M → 1B users
- **AI for SMBs** — How to rebuild with modern AI tools (Claude API, vector DBs, serverless)
- **Sources & Papers** — 6–10 real links to papers, engineering blogs, official docs
- **Interview Corner** — 3 FAANG-level questions with model answers
- **Progress Bar** — Track your journey through all 200 lessons

---

## Quick Start (5 minutes)

### 1. Clone

```bash
git clone https://github.com/originaonxi/system-design-mastery.git
cd system-design-mastery
```

### 2. Set up your email

Create a `.env` file:

```bash
cat > .env << 'EOF'
SMTP_USER=your-email@gmail.com
SMTP_PASS="your-gmail-app-password"
EMAIL_TO=your-email@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EOF
```

> **Gmail App Password:** Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) → Generate an app password for "Mail". Use that instead of your real password.

### 3. Install dependencies

```bash
pip3 install anthropic
```

### 4. Send your first lesson

```bash
source .env && python3 send_lesson.py
```

### 5. Automate (every 3 hours)

```bash
crontab -e
# Add this line:
0 */3 * * * cd /path/to/system-design-mastery && source .env && python3 send_lesson.py >> logs/cron.log 2>&1
```

That's it. You'll get 8 lessons/day, completing the full course in 25 days.

---

## Want to regenerate or customize lessons?

All 200 lessons are pre-generated in `lessons/`. But if you want to regenerate with your own customizations:

```bash
# Add your Anthropic API key to .env
echo 'ANTHROPIC_API_KEY=your-key-here' >> .env

# Regenerate all lessons (takes ~5-6 hours)
source .env && python3 generate_all.py

# Or regenerate starting from a specific lesson
source .env && python3 generate_all.py 50
```

---

## Project Structure

```
system-design-mastery/
├── .env                        # Your SMTP credentials (not in git)
├── send_lesson.py              # File-based email sender (no API needed)
├── generate_all.py             # Batch generator (uses Claude API)
├── curriculum.json             # Full 200-lesson curriculum with metadata
├── tracker.json                # Progress tracker (auto-updated)
├── templates/
│   └── newspaper.html          # HTML email template
├── lessons/
│   ├── 001.html                # Pre-generated lesson HTML
│   ├── 001.json                # Lesson metadata
│   ├── 002.html
│   └── ...                     # All 200 lessons
├── scripts/
│   └── auto_commit.sh          # Auto-push new lessons to git
└── logs/                       # Execution logs
```

---

## Built With

- **Claude API (Sonnet)** — Generates each lesson with real facts, numbers, and code
- **Python 3** — Sender + generator
- **Gmail SMTP** — Email delivery
- **Cron** — Automated scheduling
- **HTML/CSS** — Newspaper-format responsive email template

---

## Author

**Sam Anmol** — CTO @ Aonxi | Ex-Meta, Ex-Apple

Built with Claude Code (Opus 4.6)

---

## License

MIT — Use it, fork it, learn from it, teach with it.
