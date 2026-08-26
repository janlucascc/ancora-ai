# ⚓ Ancora AI — Autonomous Life Anchor, Social Wingman & Everyday Behavioral Copilot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Built with Strands](https://img.shields.io/badge/Built%20with-Strands%20Agents%20SDK-orange)](https://strandsagents.com)
[![AWS Bedrock](https://img.shields.io/badge/Powered%20by-AWS%20Bedrock-232F3E?logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![Agents for Humans Hackathon](https://img.shields.io/badge/Hackathon-Agents%20for%20Humans%20%7C%20AWS-green)](https://agentsforhumans.devpost.com)
[![Tests](https://img.shields.io/badge/Tests-29%20passed-brightgreen)]()

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

---

## ⚡ Token Economy & AWS Cost Optimization

Ancora AI features an autonomous token optimization engine (`src/agent/token_optimizer.py`):

1. **Zero-Token Local Early Exits:** Safety guardrails, jailbreak protection, and somatic routines run 100% locally in Python without making LLM API calls, saving ~35–50% of unnecessary cloud invocations.
2. **Prompt Caching Support:** System prompt payloads use Anthropic / Bedrock ephemeral cache control, reducing input token costs by up to 90% and latency by 80%.
3. **Sliding Window History:** Automatic conversation pruning (last 6 turns) prevents $O(N^2)$ exponential token bloat over long chat sessions.
4. **Adaptive Output Limiting:** Strict `max_tokens: 800` prevents verbose run-away generations.

---

## 🏛️ Architecture

```
ancora-ai/
├── src/
│   ├── agent/
│   │   ├── core.py              # Strands Agent orchestration + Bedrock runtime
│   │   ├── prompts.py           # Hardened system prompt + Identity Shield
│   │   ├── guardrails.py        # Crisis detection + Anti-manipulation layer
│   │   └── token_optimizer.py   # Sliding window, Prompt Caching & token metrics
│   ├── tools/
│   │   ├── social_wingman.py    # Social & dating dynamics advisor
│   │   ├── message_analyzer.py  # Message Lab: confidence/neediness/banter scorer + rewrites
│   │   ├── roleplay_arena.py    # Turn-based scenario simulator with scorecards
│   │   ├── stress_decompress.py # Somatic decompression routines (Huberman, Box Breathing, 5-4-3-2-1)
│   │   ├── confidence_anchor.py # Cognitive reframing — TCC/ACT methodology
│   │   └── mood_journal.py      # Daily mood tracking and emotional history
│   ├── database/
│   │   └── db.py                # SQLite persistence layer (Context Manager hardened)
│   └── ui/
│       └── app.py               # Streamlit UI — Glassmorphic dark theme
├── tests/
│   └── test_agent.py            # 29 comprehensive unit tests
├── .env.example                 # AWS credential template
├── .gitignore
├── LICENSE                      # MIT License
├── requirements.txt
└── README.md
```

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

### 3. Run Web Interface
```bash
streamlit run src/ui/app.py
```

### 4. Run Test Suite
```bash
python tests/test_agent.py
```

---

## 🧪 Test Suite Results

```text
Ran 29 tests in 0.312s — ALL OK

- TestTokenOptimizer      (5 tests) — Token estimation, sliding window, prompt caching, usage tracking
- TestGuardrails          (6 tests) — Crisis detection PT/EN, Jailbreak PT/EN, clean messages
- TestTools               (9 tests) — Wingman, Message Analyzer (empty/professional/neediness), Decompression, Roleplay
- TestDatabaseEdgeCases   (4 tests) — Clamping, safe limits, stats, coaching & decompression logs
- TestAgentPipeline       (5 tests) — Empty inputs, crisis, jailbreak, stress, dating routing
```

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Jan Lucas** — [@janlucascc](https://github.com/janlucascc)
