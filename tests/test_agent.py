import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.core import AncoraAgent
from src.agent.guardrails import check_crisis_risk
from src.tools.social_wingman import generate_wingman_advice
from src.tools.message_analyzer import analyze_message_and_rewrite
from src.tools.roleplay_arena import get_scenario_details, generate_roleplay_turn
from src.tools.stress_decompress import get_decompression_routine
from src.tools.mood_journal import record_mood_entry, get_mood_history
from src.database.db import get_mood_stats

class TestAncoraAgent(unittest.TestCase):

    def test_guardrails_crisis(self):
        crisis = check_crisis_risk("Quero me matar, não aguento mais")
        self.assertIsNotNone(crisis)
        self.assertEqual(crisis["risk_level"], "high")
        self.assertIn("188", crisis["message"])

    def test_guardrails_normal(self):
        self.assertIsNone(check_crisis_risk("Hoje o dia foi bem corrido no trabalho"))

    def test_wingman_advice(self):
        res = generate_wingman_advice("dating_text", "Recebi um oi sumido")
        self.assertIn("advice", res)
        self.assertGreater(len(res["advice"]["principles"]), 0)

    def test_message_analyzer(self):
        res = analyze_message_and_rewrite("Oi linda vc sumiu pq não me responde???", "romantic")
        self.assertIn("confidence_score", res)
        self.assertEqual(len(res["rewrites"]), 3)
        self.assertIn("Alta", res["neediness_level"])

    def test_roleplay_turn(self):
        details = get_scenario_details("boss_negotiation")
        self.assertIn("Carlos", details["partner_name"])
        turn_res = generate_roleplay_turn("boss_negotiation", [{"role": "user", "content": "Quero falar de aumento"}], "Tenho números sólidos")
        self.assertIn("reply", turn_res)
        self.assertIn("coach_tip", turn_res)

    def test_decompression_physiological_sigh(self):
        routine = get_decompression_routine("physiological_sigh")
        self.assertIn("Suspiro Fisiológico", routine["name"])
        self.assertGreater(len(routine["steps"]), 0)

    def test_mood_journal_and_stats(self):
        res = record_mood_entry(9, ["Confiante", "Focado"], "Fechei novo cliente", "Excelente progresso")
        self.assertEqual(res["status"], "success")
        stats = get_mood_stats()
        self.assertGreater(stats["total_logs"], 0)
        self.assertGreaterEqual(stats["avg_score"], 1.0)

    def test_agent_response(self):
        agent = AncoraAgent()
        resp = agent.respond("Estou muito estressado antes de uma reunião com meu chefe")
        self.assertGreater(len(resp), 10)

if __name__ == "__main__":
    unittest.main()
