import os
import time
import json
import numpy as np
from datetime import datetime
from groq import Groq
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from config import Config

class BasicRAGPipeline:
    """Pipeline 2: Vector-based RAG"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        
        self.chunks = []
        self.embeddings = []
        self.bm25 = None
        self.cache = {}
        
        self.load_documents()
    
    def load_documents(self):
        """Load and chunk all documents"""
        
        # Sample BMW luxury car data
        luxury_car_data = """
        BMW M5: The ultimate performance sedan with 625 horsepower twin-turbo engine, 0-60 in 3.0 seconds, top speed 190 mph.
        
        Ferrari F8 Tributo: Mid-engine supercar with 710 horsepower V12, 0-60 in 2.9 seconds, iconic red Italian design.
        
        Lamborghini Aventador: Super sports car with 740 HP V12 engine, 0-60 in 2.9 seconds, aggressive styling and scissor doors.
        
        Porsche 911: The legendary sports car with turbo engines, 992 generation features hybrid technology, starting at 93K USD.
        
        Mercedes-Benz AMG GT: High-performance grand tourer with 585 HP, exclusive AMG engineering, German precision.
        
        BMW History: Founded in 1916, BMW stands for Bayerische Motoren Werke (Bavarian Motor Works), known for performance and luxury.
        
        Ferrari Heritage: Since 1947, Ferrari has been the symbol of Italian excellence, racing heritage, and supercars.
        
        Lamborghini Story: Created in 1963, Lamborghini started as a tractor company before entering the exotic car market.
        
        Porsche Engineering: With over 70 years of sports car history, Porsche combines German engineering with innovation.
        
        Luxury Car Features: High-performance engines, premium interiors, advanced technology, superior handling, exclusive designs.
        
        Performance Metrics: Horsepower, 0-60 time, top speed, acceleration, braking distance, lap times on race tracks.
        
        BMW M Division: Develops high-performance M models, including M3, M5, M440i with distinctive motorsport heritage.
        
        Ferrari Models: F8 Tributo succeeds 488, Roma is 2-seat tourer, SF90 Stradale is hybrid hypercar with 1000 HP.
        
        Lamborghini Technology: Carbo-titanium construction, advanced aerodynamics, sophisticated suspension systems for handling.
        
        Porsche Variants: The 911 remains the core, Taycan is electric future, Panamera is luxury sedan, Cayenne is SUV.
        
        Pricing: BMW M5 starts around 110K, Ferrari F8 around 280K, Lamborghini Aventador around 400K, Porsche 911 from 93K.
        
        Engine Specifications: BMW M5 has twin-turbo V8, Ferrari V12 naturally aspirated, Lamborghini V12 with massive displacement.
        
        Acceleration Comparison: Most supercars achieve 0-60 in under 3 seconds, with F8 Tributo and Aventador at 2.9 seconds.
        
        Luxury Interior: Hand-stitched leather, ambient lighting, advanced infotainment, premium sound systems, bespoke customization.
        
        Sustainability: Modern luxury cars include hybrid and electric options, like BMW i8, Porsche Taycan, Ferrari hybrid models.
        """
        
        # Create chunks
        sentences = luxury_car_data.split('\n')
        for sentence in sentences:
            if sentence.strip():
                self.chunks.append(sentence.strip())
        
        # Generate embeddings
        self.embeddings = self.embedding_model.encode(self.chunks)
        
        # Initialize BM25
        tokenized_chunks = [chunk.split() for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_chunks)
        
        print(f"✅ Loaded {len(self.chunks)} document chunks for RAG")
    
    def retrieve_chunks(self, query: str, top_k: int = 5) -> list:
        """Retrieve relevant chunks using combined approach"""
        
        # Vector similarity
        query_embedding = self.embedding_model.encode([query])[0]
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * 
            np.linalg.norm(query_embedding) + 1e-10
        )
        
        # BM25 ranking
        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Combined scores (70% vector, 30% BM25)
        combined_scores = 0.7 * similarities + 0.3 * (bm25_scores / (np.max(bm25_scores) + 1e-10))
        
        # Get top-k
        top_indices = np.argsort(combined_scores)[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices if combined_scores[i] > 0.1]
    
    def query(self, question: str) -> dict:
        """Execute Basic RAG query"""
        
        cache_key = f"rag_basic_{hash(question)}"
        if Config.ENABLE_CACHING and cache_key in self.cache:
            return self.cache[cache_key]
        
        start_time = time.time()
        
        try:
            # Retrieve relevant chunks
            relevant_chunks = self.retrieve_chunks(question, top_k=5)
            context = "\n".join(relevant_chunks)
            
            # Build prompt with context
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a luxury car expert. Use the following information to answer the question.

REFERENCE INFORMATION:
{context}

QUESTION: {question}

Answer based on the provided information. Be specific and detailed."""
                    }
                ]
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            answer = message.choices[0].message.content
            prompt_tokens = message.usage.prompt_tokens
            completion_tokens = message.usage.completion_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            result = {
                "pipeline": "Basic RAG",
                "answer": answer,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                },
                "latency_seconds": round(latency, 2),
                "cost": self.calculate_cost(prompt_tokens, completion_tokens),
                "retrieved_chunks": len(relevant_chunks),
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "status": "success"
            }
            
            if Config.ENABLE_CACHING:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            return {
                "pipeline": "Basic RAG",
                "answer": f"Error: {str(e)}",
                "tokens": {"prompt": 0, "completion": 0, "total": 0},
                "latency_seconds": 0,
                "cost": 0,
                "retrieved_chunks": 0,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate API cost"""
        input_cost = (prompt_tokens / 1_000_000) * 0.27
        output_cost = (completion_tokens / 1_000_000) * 0.27
        return round(input_cost + output_cost, 6)
