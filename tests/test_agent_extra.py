import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.agent.core import AncoraAgent

class TestAgentPipelineExtra(unittest.TestCase):
    def test_generate_chat_title(self):
        agent = AncoraAgent(model_id="offline")
        title = agent.generate_chat_title("Quero falar sobre a minha ansiedade no trabalho de hoje")
        self.assertIn("Quero falar sobre", title)
        
        title2 = agent.generate_chat_title("   ")
        self.assertEqual(title2, "Nova Conversa")

if __name__ == "__main__":
    unittest.main()
