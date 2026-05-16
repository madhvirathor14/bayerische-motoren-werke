import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration for BMW GraphRAG Project"""
    
    # Project Settings
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Bayerische Motoren Werke")
    PROJECT_DESCRIPTION = os.getenv(
        "PROJECT_DESCRIPTION",
        "GraphRAG-Powered Luxury Car Knowledge Engine"
    )
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Settings
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    
    # Data Paths
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    RAW_DOCUMENTS_DIR = os.path.join(DATA_DIR, "raw_documents")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    CACHE_DIR = os.getenv("CACHE_DIR", "./cache")
    
    # Create directories if they don't exist
    os.makedirs(RAW_DOCUMENTS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Evaluation Settings
    LLM_JUDGE_MODEL = os.getenv("LLM_JUDGE_MODEL", "mixtral-8x7b-32768")
    BERTSCORE_MODEL = os.getenv("BERTSCORE_MODEL", "all-mpnet-base-v2")
    ACCURACY_THRESHOLD = float(os.getenv("ACCURACY_THRESHOLD", 0.7))
    
    # Benchmark Settings
    NUM_TEST_QUERIES = int(os.getenv("NUM_TEST_QUERIES", 20))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 60))
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    
    # Luxury Car Brands & Models
    CAR_BRANDS = {
        "BMW": {
            "models": ["M5", "M3", "X7", "7 Series", "i8"],
            "country": "Germany",
            "founded": 1916,
            "specialty": "Performance & Luxury"
        },
        "Ferrari": {
            "models": ["F8 Tributo", "SF90 Stradale", "Roma", "Portofino"],
            "country": "Italy",
            "founded": 1947,
            "specialty": "Supercars & Racing"
        },
        "Lamborghini": {
            "models": ["Aventador", "Huracan", "Revuelto", "Urus"],
            "country": "Italy",
            "founded": 1963,
            "specialty": "Ultra-High Performance"
        },
        "Porsche": {
            "models": ["911", "Taycan", "Panamera", "Cayenne"],
            "country": "Germany",
            "founded": 1931,
            "specialty": "Sports & Engineering"
        },
        "Mercedes-Benz": {
            "models": ["AMG GT", "S-Class", "G-Class", "EQS"],
            "country": "Germany",
            "founded": 1926,
            "specialty": "Luxury & Innovation"
        }
    }
    
    # Test Queries for Benchmarking
    TEST_QUERIES = [
        "Compare BMW M5 and Ferrari F8 Tributo in terms of performance",
        "What is the acceleration time of Lamborghini Aventador?",
        "Which luxury car has the most powerful engine?",
        "Tell me about Porsche 911 evolution and history",
        "What makes Mercedes-Benz special in luxury segment?",
        "How much does a Ferrari Roma cost?",
        "Explain the difference between BMW M3 and M5",
        "What are the features of Lamborghini Urus?",
        "How fast is a Porsche Taycan?",
        "What is special about Mercedes-Benz G-Class?"
    ]
