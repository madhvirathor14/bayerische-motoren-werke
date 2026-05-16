#!/usr/bin/env python3
"""
Test Script for BMW GraphRAG Project
Verifies all components are working before running the main app
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_ok(text):
    print(f"✅ {text}")

def print_warn(text):
    print(f"⚠️  {text}")

def print_error(text):
    print(f"❌ {text}")

def test_imports():
    """Test if all required modules can be imported"""
    print_header("Testing Imports")
    
    required_modules = [
        'streamlit',
        'plotly',
        'groq',
        'sentence_transformers',
        'bert_score',
        'pandas',
        'numpy',
        'dotenv'
    ]
    
    failed = []
    
    for module in required_modules:
        try:
            __import__(module)
            print_ok(f"Module: {module}")
        except ImportError as e:
            print_error(f"Module: {module} - {str(e)}")
            failed.append(module)
    
    return len(failed) == 0

def test_config():
    """Test if configuration can be loaded"""
    print_header("Testing Configuration")
    
    try:
        from config import Config
        print_ok(f"Project Name: {Config.PROJECT_NAME}")
        print_ok(f"GROQ Model: {Config.GROQ_MODEL}")
        print_ok(f"Embedding Model: {Config.EMBEDDING_MODEL}")
        
        if not Config.GROQ_API_KEY:
            print_error("GROQ_API_KEY not configured in .env")
            return False
        
        print_ok("GROQ_API_KEY: ••••••••••••••••• (hidden)")
        return True
        
    except Exception as e:
        print_error(f"Configuration error: {str(e)}")
        return False

def test_directories():
    """Test if data directories exist"""
    print_header("Testing Directories")
    
    dirs = [
        'data',
        'data/raw_documents',
        'data/images',
        'cache',
        'pipelines',
        'evaluation'
    ]
    
    all_ok = True
    for dir_path in dirs:
        if os.path.isdir(dir_path):
            print_ok(f"Directory: {dir_path}")
        else:
            print_warn(f"Directory missing: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print_ok(f"Created: {dir_path}")
    
    return all_ok

def test_pipelines():
    """Test if pipelines can be initialized"""
    print_header("Testing Pipelines")
    
    try:
        from config import Config
        from pipelines import LLMOnlyPipeline, BasicRAGPipeline, GraphRAGPipeline
        
        print("Initializing LLM-Only Pipeline...")
        llm_pipeline = LLMOnlyPipeline()
        print_ok("LLM-Only Pipeline initialized")
        
        print("Initializing Basic RAG Pipeline...")
        rag_pipeline = BasicRAGPipeline()
        print_ok("Basic RAG Pipeline initialized")
        
        print("Initializing GraphRAG Pipeline...")
        graph_pipeline = GraphRAGPipeline()
        print_ok("GraphRAG Pipeline initialized")
        
        return True
        
    except Exception as e:
        print_error(f"Pipeline initialization failed: {str(e)}")
        return False

def test_api_connectivity():
    """Test if GROQ API is reachable"""
    print_header("Testing API Connectivity")
    
    try:
        from config import Config
        from groq import Groq
        
        client = Groq(api_key=Config.GROQ_API_KEY)
        
        print("Testing GROQ API connectivity...")
        
        # Make a simple test call
        message = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Hello, BMW GraphRAG!'"}
            ]
        )
        
        response = message.choices[0].message.content
        if "BMW" in response or "Hello" in response:
            print_ok(f"API Response: {response}")
            return True
        else:
            print_error(f"Unexpected response: {response}")
            return False
            
    except Exception as e:
        print_error(f"API connectivity test failed: {str(e)}")
        print("  Check:")
        print("  1. GROQ_API_KEY is valid (get from https://console.groq.com)")
        print("  2. Internet connection is working")
        print("  3. GROQ service is not down")
        return False

def test_demo_query():
    """Test a simple query through all pipelines"""
    print_header("Testing Demo Query")
    
    try:
        from config import Config
        from pipelines import LLMOnlyPipeline, BasicRAGPipeline, GraphRAGPipeline
        
        test_query = "What is BMW?"
        
        print(f"Test Query: '{test_query}'")
        print()
        
        print("Running LLM-Only Pipeline...")
        llm_pipeline = LLMOnlyPipeline()
        result = llm_pipeline.query(test_query)
        
        if result['status'] == 'success':
            print_ok(f"LLM-Only: {result['tokens']['total']} tokens, {result['latency_seconds']}s")
        else:
            print_error(f"LLM-Only failed: {result.get('error', 'Unknown error')}")
            return False
        
        print("Running Basic RAG Pipeline...")
        rag_pipeline = BasicRAGPipeline()
        result = rag_pipeline.query(test_query)
        
        if result['status'] == 'success':
            print_ok(f"Basic RAG: {result['tokens']['total']} tokens, {result['latency_seconds']}s")
        else:
            print_error(f"Basic RAG failed: {result.get('error', 'Unknown error')}")
            return False
        
        print("Running GraphRAG Pipeline...")
        graph_pipeline = GraphRAGPipeline()
        result = graph_pipeline.query(test_query)
        
        if result['status'] == 'success':
            print_ok(f"GraphRAG: {result['tokens']['total']} tokens, {result['latency_seconds']}s")
        else:
            print_error(f"GraphRAG failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Demo query test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🚗 BMW GraphRAG Project - Setup Verification              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Directories", test_directories),
        ("Pipelines", test_pipelines),
        ("API Connectivity", test_api_connectivity),
        ("Demo Query", test_demo_query),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🚀 You're ready to run the app!")
        print("\n   Command: streamlit run app.py")
        print("\n")
        return 0
    else:
        print("\n" + "="*60)
        print("❌ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the errors above and run this test again.")
        print("\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
