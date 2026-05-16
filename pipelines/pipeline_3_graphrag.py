import time
import json
import re
from datetime import datetime
from groq import Groq
from config import Config

class GraphRAGPipeline:
    """Pipeline 3: GraphRAG simulation with entity-relationship extraction"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.cache = {}
        self.knowledge_graph = self.initialize_graph()
    
    def initialize_graph(self) -> dict:
        """Initialize knowledge graph with luxury car entities and relationships"""
        
        graph = {
            "entities": {
                "BMW": {
                    "type": "Brand",
                    "country": "Germany",
                    "founded": 1916,
                    "models": ["M5", "M3", "X7", "7 Series", "i8"]
                },
                "Ferrari": {
                    "type": "Brand",
                    "country": "Italy",
                    "founded": 1947,
                    "models": ["F8 Tributo", "SF90 Stradale", "Roma", "Portofino"]
                },
                "Lamborghini": {
                    "type": "Brand",
                    "country": "Italy",
                    "founded": 1963,
                    "models": ["Aventador", "Huracan", "Revuelto", "Urus"]
                },
                "Porsche": {
                    "type": "Brand",
                    "country": "Germany",
                    "founded": 1931,
                    "models": ["911", "Taycan", "Panamera", "Cayenne"]
                },
                "Mercedes-Benz": {
                    "type": "Brand",
                    "country": "Germany",
                    "founded": 1926,
                    "models": ["AMG GT", "S-Class", "G-Class", "EQS"]
                },
                "M5": {
                    "type": "Model",
                    "brand": "BMW",
                    "horsepower": 625,
                    "acceleration_0_60": 3.0,
                    "top_speed": 190,
                    "price": 110000,
                    "engine": "Twin-Turbo V8"
                },
                "F8 Tributo": {
                    "type": "Model",
                    "brand": "Ferrari",
                    "horsepower": 710,
                    "acceleration_0_60": 2.9,
                    "top_speed": 211,
                    "price": 280000,
                    "engine": "V12"
                },
                "Aventador": {
                    "type": "Model",
                    "brand": "Lamborghini",
                    "horsepower": 740,
                    "acceleration_0_60": 2.9,
                    "top_speed": 217,
                    "price": 400000,
                    "engine": "V12"
                },
                "911": {
                    "type": "Model",
                    "brand": "Porsche",
                    "horsepower": 450,
                    "acceleration_0_60": 3.5,
                    "top_speed": 183,
                    "price": 93000,
                    "engine": "Twin-Turbo Flat-6"
                }
            },
            "relationships": [
                {"from": "BMW", "to": "M5", "type": "MANUFACTURES"},
                {"from": "BMW", "to": "M3", "type": "MANUFACTURES"},
                {"from": "Ferrari", "to": "F8 Tributo", "type": "MANUFACTURES"},
                {"from": "Ferrari", "to": "SF90 Stradale", "type": "MANUFACTURES"},
                {"from": "Lamborghini", "to": "Aventador", "type": "MANUFACTURES"},
                {"from": "Lamborghini", "to": "Huracan", "type": "MANUFACTURES"},
                {"from": "Porsche", "to": "911", "type": "MANUFACTURES"},
                {"from": "Porsche", "to": "Taycan", "type": "MANUFACTURES"},
                {"from": "M5", "to": "F8 Tributo", "type": "COMPETES_WITH"},
                {"from": "Aventador", "to": "F8 Tributo", "type": "COMPETES_WITH"},
                {"from": "BMW", "to": "Mercedes-Benz", "type": "COMPETITOR"},
                {"from": "BMW", "to": "Porsche", "type": "COMPETITOR"},
                {"from": "M5", "to": "Aventador", "type": "SIMILAR_SEGMENT"},
                {"from": "F8 Tributo", "to": "Aventador", "type": "SIMILAR_SEGMENT"}
            ]
        }
        
        return graph
    
    def extract_entities(self, query: str) -> list:
        """Extract car entities mentioned in query"""
        
        entities = []
        for entity_name in self.knowledge_graph["entities"].keys():
            if entity_name.lower() in query.lower():
                entities.append(entity_name)
        
        return entities
    
    def find_relationships(self, entities: list) -> list:
        """Find relationships between extracted entities"""
        
        relationships = []
        for rel in self.knowledge_graph["relationships"]:
            if rel["from"] in entities or rel["to"] in entities:
                relationships.append(rel)
        
        return relationships
    
    def build_graph_context(self, entities: list, relationships: list) -> str:
        """Build structured context from graph data"""
        
        context = "KNOWLEDGE GRAPH CONTEXT:\n\n"
        
        if entities:
            context += "Relevant Entities:\n"
            for entity in entities:
                if entity in self.knowledge_graph["entities"]:
                    data = self.knowledge_graph["entities"][entity]
                    context += f"\n{entity} ({data.get('type', 'Unknown')}):\n"
                    for key, value in data.items():
                        if key != "type":
                            context += f"  - {key}: {value}\n"
        
        if relationships:
            context += "\nEntity Relationships:\n"
            for rel in relationships:
                context += f"  - {rel['from']} --[{rel['type']}]--> {rel['to']}\n"
        
        return context
    
    def query(self, question: str) -> dict:
        """Execute GraphRAG query"""
        
        cache_key = f"graphrag_{hash(question)}"
        if Config.ENABLE_CACHING and cache_key in self.cache:
            return self.cache[cache_key]
        
        start_time = time.time()
        
        try:
            # Step 1: Entity Extraction
            entities = self.extract_entities(question)
            
            # Step 2: Relationship Finding
            relationships = self.find_relationships(entities)
            
            # Step 3: Build Graph Context
            graph_context = self.build_graph_context(entities, relationships)
            
            # Step 4: LLM generates answer with graph context
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": f"""{graph_context}

Question: {question}

Based on the knowledge graph information above, provide a detailed and accurate answer. Include specific data points when available."""
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
                "pipeline": "GraphRAG",
                "answer": answer,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                },
                "latency_seconds": round(latency, 2),
                "cost": self.calculate_cost(prompt_tokens, completion_tokens),
                "entities_extracted": len(entities),
                "relationships_found": len(relationships),
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "status": "success"
            }
            
            if Config.ENABLE_CACHING:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            return {
                "pipeline": "GraphRAG",
                "answer": f"Error: {str(e)}",
                "tokens": {"prompt": 0, "completion": 0, "total": 0},
                "latency_seconds": 0,
                "cost": 0,
                "entities_extracted": 0,
                "relationships_found": 0,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate API cost"""
        input_cost = (prompt_tokens / 1_000_000) * 0.27
        output_cost = (completion_tokens / 1_000_000) * 0.27
        return round(input_cost + output_cost, 6)
