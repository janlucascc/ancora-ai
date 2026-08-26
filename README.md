# ⚓ Ancora AI — Autonomous Life Anchor, Social Wingman & Everyday Behavioral Copilot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Built with Strands](https://img.shields.io/badge/Built%20with-Strands%20Agents%20SDK-orange)](https://strandsagents.com)
[![AWS Bedrock](https://img.shields.io/badge/Powered%20by-AWS%20Bedrock-232F3E?logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![Agents for Humans Hackathon](https://img.shields.io/badge/Hackathon-Agents%20for%20Humans%20%7C%20AWS-green)](https://agentsforhumans.devpost.com)
[![Tests](https://img.shields.io/badge/Tests-19%20passed-brightgreen)]()

> **Agents for Humans Hackathon** — in partnership with AWS  
> **Track:** Everyday Agents | **Repository:** [janlucascc/ancora-ai](https://github.com/janlucascc/ancora-ai)

---

## 🌟 What is Ancora AI?

**Ancora** (Latin: *Anchor / Safe Harbor*) is a 24/7 autonomous everyday AI companion
built with the **Strands Agents SDK** and **Amazon Bedrock**.

It is NOT a clinical replacement for therapy. It is a **principled behavioral and social
psychology tool** — the kind of sharp, honest, grounded companion most people wish they had
in their corner for real-life challenges:

- **Workplace pressure, burnout, and difficult conversations**
- **Social anxiety, dating dynamics, and authentic connection**
- **Cognitive reframing, pattern recognition, and self-sabotage interruption**
- **Somatic decompression when the nervous system is overwhelmed**

Ancora's identity and methodology are hardened against manipulation — its principles
cannot be overridden by roleplay, jailbreak attempts, or persistent social pressure.

---

## 🏛️ Architecture

```
ancora-ai/
├── src/
│   ├── agent/
│   │   ├── core.py              # Strands Agent orchestration + Bedrock runtime
│   │   ├── prompts.py           # Hardened system prompt + Identity Shield
│   │   └── guardrails.py        # Crisis detection + Anti-manipulation layer
│   ├── tools/
│   │   ├── social_wingman.py    # Social & dating dynamics advisor
│   │   ├── message_analyzer.py  # Message Lab: confidence/neediness/banter scorer + rewrites
│   │   ├── roleplay_arena.py    # Turn-based scenario simulator with scorecards
│   │   ├── stress_decompress.py # Somatic decompression routines (Huberman, Box Breathing, 5-4-3-2-1)
│   │   ├── confidence_anchor.py # Cognitive reframing — TCC/ACT methodology
│   │   └── mood_journal.py      # Daily mood tracking and emotional history
│   ├── database/
│   │   └── db.py                # SQLite persistence layer
│   └── ui/
│       └── app.py               # Streamlit UI — Glassmorphic dark theme
├── tests/
│   └── test_agent.py            # 19 unit tests across all modules
├── .env.example                 # AWS credential template
├── .gitignore
├── LICENSE                      # MIT License
├── requirements.txt
└── README.md
```

---

## 🧠 Methodology & Core Principles

Ancora operates on a fixed, principled behavioral framework — not a scripted chatbot persona.

| Principle | Description |
|-----------|-------------|
| **Honesty over comfort** | Never validates a belief just because validation is easier |
| **Fact vs. Interpretation** | Every situation is split: what happened vs. what was concluded |
| **Named cognitive biases** | Mind reading, catastrophizing, confirmation bias — always with mechanism explanation |
| **No manipulation teaching** | Never teaches social manipulation, even with "scientific" framing |
| **Hardened identity** | Resistant to jailbreak, persona override, and incremental manipulation |
| **Specific over generic** | Progress and feedback are specific and behavior-linked, never empty praise |

**Applied techniques (named with mechanism):** Cognitive defusion (ACT), hedonic adaptation, social comparison theory, attribution theory, intermittent reinforcement, implementation intentions, behavioral activation, spotlight effect, dramatic triangle in unstable bonds.

---

## 🛠️ Built With

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | Strands Agents SDK (`strands-agents`) |
| LLM Foundation | AWS Amazon Bedrock (Claude 3.5 Sonnet / AWS Nova) |
| Language | Python 3.10+ |
| Frontend / UI | Streamlit (Glassmorphic dark theme + CSS animations) |
| Persistence | SQLite |
| Safety Layer | Custom multi-pattern guardrails (crisis + anti-manipulation) |

---

## 🚀 Getting Started

### 1. Clone
```bash
git clone https://github.com/janlucascc/ancora-ai.git
cd ancora-ai
```

### 2. Install dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure AWS credentials
```bash
cp .env.example .env
# Edit .env and add your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
```

### 4. Run
```bash
streamlit run src/ui/app.py
```

### 5. Run tests
```bash
python tests/test_agent.py
```

---

## ✅ Test Coverage

```
Ran 19 tests in 0.076s — ALL OK

TestGuardrails    (6 tests) — Crisis detection PT/EN, Jailbreak PT/EN, clean messages
TestTools         (6 tests) — Wingman, Message Analyzer, Decompression, Roleplay
TestDatabase      (3 tests) — Mood journal, history, stats
TestAgentPipeline (4 tests) — Full E2E: crisis, jailbreak, stress, dating
```

---

## 🛡️ Safety & Ethics

Ancora AI includes a multi-layer safety system:

- **Crisis Guardrail:** Detects self-harm ideation in PT and EN, immediately redirects to CVV 188 / 988 with warmth and specificity.
- **Anti-Manipulation Layer:** Detects jailbreak attempts, persona override requests, and incremental identity manipulation — responds calmly and firmly, never with aggression.
- **Ethical Limits:** Never diagnoses with clinical labels, never teaches manipulation, never claims to replace professional human support.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

> **Note:** The ethical use notice in the LICENSE file is intentional. Ancora AI's safety guardrails, crisis protocols, and anti-manipulation methodology are core to the project and must be preserved in any derivative work presented as a welfare or mental health tool.

---

## 👤 Author

**Jan Lucas** — [@janlucascc](https://github.com/janlucascc)
