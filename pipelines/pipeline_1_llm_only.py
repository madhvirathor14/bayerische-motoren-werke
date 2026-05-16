import time
import json
from datetime import datetime
from groq import Groq
from config import Config

class LLMOnlyPipeline:
    """Pipeline 1: Pure LLM without retrieval - Baseline"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.cache = {}
    
    def query(self, question: str) -> dict:
        """Execute LLM-Only query"""
        
        # Check cache
        cache_key = f"llm_only_{hash(question)}"
        if Config.ENABLE_CACHING and cache_key in self.cache:
            return self.cache[cache_key]
        
        start_time = time.time()
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are an expert automotive specialist with deep knowledge about luxury cars.

Question: {question}

Provide a detailed, accurate answer about luxury cars. Include specific details, specifications, or information you know about the car(s) mentioned."""
                    }
                ]
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Extract response
            answer = message.choices[0].message.content
            
            # Calculate tokens (Groq provides this)
            prompt_tokens = message.usage.prompt_tokens
            completion_tokens = message.usage.completion_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            result = {
                "pipeline": "LLM-Only",
                "answer": answer,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                },
                "latency_seconds": round(latency, 2),
                "cost": self.calculate_cost(prompt_tokens, completion_tokens),
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "status": "success"
            }
            
            # Cache result
            if Config.ENABLE_CACHING:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            return {
                "pipeline": "LLM-Only",
                "answer": f"Error: {str(e)}",
                "tokens": {"prompt": 0, "completion": 0, "total": 0},
                "latency_seconds": 0,
                "cost": 0,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Groq Mixtral-8x7b pricing (approximately):
        Input: $0.27 per 1M tokens
        Output: $0.27 per 1M tokens
        """
        input_cost = (prompt_tokens / 1_000_000) * 0.27
        output_cost = (completion_tokens / 1_000_000) * 0.27
        return round(input_cost + output_cost, 6)
