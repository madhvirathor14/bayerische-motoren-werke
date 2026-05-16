import numpy as np
from sentence_transformers import SentenceTransformer, util
from groq import Groq
from config import Config

class AccuracyEvaluator:
    """Evaluate answer quality using LLM-as-Judge and BERTScore"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        self.bert_model = SentenceTransformer(Config.BERTSCORE_MODEL)
    
    def llm_as_judge(self, question: str, answer: str, reference: str = None) -> dict:
        """
        Use LLM to evaluate if answer is accurate
        Returns PASS or FAIL verdict
        """
        
        prompt = f"""You are an expert judge for luxury car knowledge.

QUESTION: {question}
ANSWER: {answer}
"""
        
        if reference:
            prompt += f"REFERENCE: {reference}\n\n"
        
        prompt += """Evaluate if the answer is:
1. Accurate and factually correct
2. Relevant to the question
3. Complete and detailed

Respond with only:
PASS - if answer is accurate and relevant
FAIL - if answer is inaccurate, irrelevant, or missing key information

Judgment:"""
        
        try:
            response = self.groq_client.messages.create(
                model=Config.LLM_JUDGE_MODEL,
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            judgment = response.content[0].text.strip().split('\n')[0]
            
            return {
                "verdict": judgment,
                "passed": "PASS" in judgment.upper(),
                "confidence": 0.95,
                "status": "success"
            }
        except Exception as e:
            return {
                "verdict": "ERROR",
                "passed": False,
                "error": str(e),
                "status": "error"
            }
    
    def bertscore(self, generated: str, reference: str) -> dict:
        """
        Calculate semantic similarity using BERTScore
        Returns similarity score 0-1
        """
        
        try:
            gen_embedding = self.bert_model.encode(generated, convert_to_tensor=True)
            ref_embedding = self.bert_model.encode(reference, convert_to_tensor=True)
            
            # Cosine similarity
            similarity = util.pytorch_cos_sim(gen_embedding, ref_embedding).item()
            
            # Interpret similarity
            if similarity > 0.7:
                quality = "Excellent"
            elif similarity > 0.5:
                quality = "Good"
            elif similarity > 0.3:
                quality = "Fair"
            else:
                quality = "Poor"
            
            return {
                "score": round(similarity, 4),
                "quality": quality,
                "status": "success"
            }
        except Exception as e:
            return {
                "score": 0,
                "quality": "Error",
                "error": str(e),
                "status": "error"
            }
    
    def evaluate(self, question: str, generated_answer: str, 
                reference_answer: str = None) -> dict:
        """
        Combined evaluation using both methods
        """
        
        judge_result = self.llm_as_judge(question, generated_answer, reference_answer)
        
        if reference_answer:
            bert_result = self.bertscore(generated_answer, reference_answer)
        else:
            bert_result = {"score": 0, "quality": "N/A", "status": "skipped"}
        
        # Combined accuracy score
        judge_score = 1.0 if judge_result.get("passed") else 0.0
        bert_score = bert_result.get("score", 0) / 1.0  # Normalize to 0-1
        
        # Weight: 60% judge, 40% BERT (when both available)
        if bert_result.get("status") == "success":
            combined_accuracy = (judge_score * 0.6) + (bert_score * 0.4)
        else:
            combined_accuracy = judge_score
        
        return {
            "judge": judge_result,
            "bertscore": bert_result,
            "combined_accuracy": round(combined_accuracy, 4),
            "passed": judge_result.get("passed", False),
            "timestamp": datetime.now().isoformat()
        }


from datetime import datetime
