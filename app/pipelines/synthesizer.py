import os
import json
from groq import Groq

class RemediationSynthesizer:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None

    def synthesize(self, clean_log: str, retrieved_contexts: list[str]):
        context_block = "\n---\n".join(retrieved_contexts) if retrieved_contexts else "No historical post-mortems found."
        
        if not self.client:
            return {
                "diagnosed_root_cause": "Groq API key not configured in environment variables.",
                "remediation_steps": ["1. Set the GROQ_API_KEY environment variable in your terminal."],
                "strict_context_used": context_block
            }
        
        prompt = f"""
        You are an expert SRE assistant. Analyze the incoming error log using the provided historical context.
        
        Incoming Log:
        {clean_log}
        
        Historical Post-Mortem Context:
        {context_block}
        
        Return a JSON object with exactly two keys:
        1. "diagnosed_root_cause": A string explaining the root cause.
        2. "remediation_steps": An array of strings outlining clear action steps.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["strict_context_used"] = context_block
            return result
        except Exception as e:
            return {
                "diagnosed_root_cause": f"Groq Model Error: {str(e)}",
                "remediation_steps": ["1. Verify your Groq console dashboard settings and API key permissions."],
                "strict_context_used": context_block
            }