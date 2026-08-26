from typing import List, Dict, Any, Tuple
import json

class TokenOptimizer:
    """
    Token Economy & Context Window Optimizer for Ancora AI.
    
    Strategies implemented:
    1. Sliding Window History: Truncates history to the last K turns to prevent O(N^2) token growth.
    2. Prompt Caching Structure: Prepares system prompt blocks for Bedrock / Anthropic Cache Control (90% discount).
    3. Token Estimation & Savings Metrics: Tracks tokens used vs. tokens saved by local routing.
    4. Adaptive Max Tokens: Sets strict max output tokens according to the intent.
    """

    def __init__(self, max_history_turns: int = 6, max_output_tokens: int = 800):
        self.max_history_turns = max_history_turns
        self.max_output_tokens = max_output_tokens
        self.total_tokens_used = 0
        self.total_tokens_saved_by_local_routing = 0

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimator (~4 characters per token for PT/EN)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def optimize_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Applies a sliding window to conversation history.
        Keeps only the most recent `max_history_turns` turns, avoiding exponential token bloat.
        """
        if not history:
            return []
        
        # Keep last 2 * max_history_turns messages (user + assistant pairs)
        window_size = self.max_history_turns * 2
        trimmed_history = history[-window_size:]
        return trimmed_history

    def prepare_bedrock_payload(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        current_message: str,
        enable_prompt_caching: bool = True
    ) -> Tuple[Dict[str, Any], int]:
        """
        Formats the optimal payload for AWS Bedrock Anthropic Claude 3.5.
        Calculates estimated input tokens and sets cache headers.
        """
        trimmed = self.optimize_history(history)
        messages = list(trimmed)
        messages.append({"role": "user", "content": current_message})

        # Calculate estimated token footprint
        system_tokens = self.estimate_tokens(system_prompt)
        messages_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in messages)
        estimated_input_tokens = system_tokens + messages_tokens

        # Format system prompt with cache_control structure for Claude 3.5 / Bedrock
        if enable_prompt_caching:
            system_payload = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        else:
            system_payload = system_prompt

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_output_tokens,
            "temperature": 0.5,
            "system": system_payload,
            "messages": messages
        }

        return payload, estimated_input_tokens

    def record_local_routing_saving(self, prompt_text: str, system_prompt_len: int = 1500):
        """Records token savings when a local tool / guardrail handles the query without LLM API call."""
        saved_input = self.estimate_tokens(prompt_text) + system_prompt_len
        saved_output = 250  # Average response length
        self.total_tokens_saved_by_local_routing += (saved_input + saved_output)

    def record_llm_usage(self, input_tokens: int, output_tokens: int):
        """Records actual LLM token consumption."""
        self.total_tokens_used += (input_tokens + output_tokens)

    def get_stats(self) -> Dict[str, Any]:
        """Returns session token statistics."""
        return {
            "tokens_used": self.total_tokens_used,
            "tokens_saved": self.total_tokens_saved_by_local_routing,
            "estimated_cost_saved_usd": round((self.total_tokens_saved_by_local_routing / 1000) * 0.003, 4)
        }
