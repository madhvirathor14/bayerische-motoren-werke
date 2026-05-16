import json
from datetime import datetime
from typing import List, Dict

class MetricsTracker:
    """Track and analyze metrics from all pipelines"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, result: dict):
        """Add pipeline result"""
        self.results.append(result)
    
    def calculate_comparison(self) -> dict:
        """Calculate comparison metrics between pipelines"""
        
        if not self.results:
            return {}
        
        comparison = {}
        
        # Group results by pipeline
        pipelines = {}
        for result in self.results:
            pipeline = result.get("pipeline", "Unknown")
            if pipeline not in pipelines:
                pipelines[pipeline] = []
            pipelines[pipeline].append(result)
        
        # Calculate averages
        for pipeline, results in pipelines.items():
            avg_tokens = sum(r["tokens"]["total"] for r in results) / len(results)
            avg_latency = sum(r["latency_seconds"] for r in results) / len(results)
            avg_cost = sum(r["cost"] for r in results) / len(results)
            
            comparison[pipeline] = {
                "avg_tokens": round(avg_tokens),
                "avg_latency": round(avg_latency, 2),
                "avg_cost": round(avg_cost, 6),
                "total_queries": len(results)
            }
        
        # Calculate reductions (vs Basic RAG baseline)
        if "Basic RAG" in comparison:
            baseline_tokens = comparison["Basic RAG"]["avg_tokens"]
            baseline_latency = comparison["Basic RAG"]["avg_latency"]
            baseline_cost = comparison["Basic RAG"]["avg_cost"]
            
            for pipeline in comparison:
                if pipeline != "Basic RAG":
                    token_reduction = (
                        (baseline_tokens - comparison[pipeline]["avg_tokens"]) / baseline_tokens
                    ) * 100 if baseline_tokens > 0 else 0
                    
                    latency_improvement = (
                        (baseline_latency - comparison[pipeline]["avg_latency"]) / baseline_latency
                    ) * 100 if baseline_latency > 0 else 0
                    
                    cost_savings = (
                        (baseline_cost - comparison[pipeline]["avg_cost"]) / baseline_cost
                    ) * 100 if baseline_cost > 0 else 0
                    
                    comparison[pipeline]["token_reduction_percent"] = round(token_reduction, 2)
                    comparison[pipeline]["latency_improvement_percent"] = round(latency_improvement, 2)
                    comparison[pipeline]["cost_savings_percent"] = round(cost_savings, 2)
        
        return comparison
    
    def get_best_pipeline(self, metric: str = "token_reduction_percent") -> str:
        """Get best performing pipeline for a metric"""
        
        comparison = self.calculate_comparison()
        best = None
        best_value = float('-inf')
        
        for pipeline, metrics in comparison.items():
            if metric in metrics:
                if metrics[metric] > best_value:
                    best_value = metrics[metric]
                    best = pipeline
        
        return best
    
    def export_json(self, filename: str = "benchmark_results.json"):
        """Export results to JSON"""
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(self.results),
            "results": self.results,
            "comparison": self.calculate_comparison()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    def print_summary(self):
        """Print summary to console"""
        
        comparison = self.calculate_comparison()
        
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY - Bayerische Motoren Werke GraphRAG Project")
        print("="*70 + "\n")
        
        for pipeline, metrics in comparison.items():
            print(f"\n📊 {pipeline}")
            print("-" * 70)
            print(f"  Average Tokens:        {metrics['avg_tokens']:,}")
            print(f"  Average Latency:       {metrics['avg_latency']}s")
            print(f"  Average Cost:          ${metrics['avg_cost']:.6f}")
            print(f"  Total Queries:         {metrics['total_queries']}")
            
            if "token_reduction_percent" in metrics:
                print(f"  Token Reduction:       {metrics['token_reduction_percent']}% vs Basic RAG")
                print(f"  Latency Improvement:   {metrics['latency_improvement_percent']}% vs Basic RAG")
                print(f"  Cost Savings:          {metrics['cost_savings_percent']}% vs Basic RAG")
        
        print("\n" + "="*70)
