import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.core import AncoraAgent
from src.agent.guardrails import check_crisis_risk
from src.tools.social_wingman import generate_wingman_advice
from src.tools.stress_decompress import get_decompression_routine
from src.tools.mood_journal import record_mood_entry, get_mood_history

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

    def test_decompression(self):
        routine = get_decompression_routine("box_breathing")
        self.assertIn("Respiração Quadrada", routine["name"])
        self.assertGreater(len(routine["steps"]), 0)

    def test_mood_journal_db(self):
        res = record_mood_entry(8, ["Confiante", "Animado"], "Fechei um projeto", "Dia muito produtivo")
        self.assertEqual(res["status"], "success")
        history = get_mood_history(limit=5)
        self.assertGreater(len(history), 0)

    def test_agent_response(self):
        agent = AncoraAgent()
        resp = agent.respond("Estou muito estressado antes de uma reunião com meu chefe")
        self.assertGreater(len(resp), 10)

if __name__ == "__main__":
    unittest.main()
