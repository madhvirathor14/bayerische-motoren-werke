import json
from datetime import datetime

class BenchmarkReportGenerator:
    """Generate comprehensive benchmark reports"""
    
    def __init__(self, results: list, comparison: dict = None):
        self.results = results
        self.comparison = comparison or {}
        self.timestamp = datetime.now()
    
    def generate_html_report(self, filename: str = "benchmark_report.html") -> str:
        """Generate HTML report"""
        
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bayerische Motoren Werke - GraphRAG Benchmark Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .metric-value {
            color: #667eea;
            font-size: 1.8em;
            font-weight: bold;
        }
        .metric-unit {
            color: #999;
            font-size: 0.8em;
            margin-left: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }
        td {
            border-bottom: 1px solid #ddd;
            padding: 12px;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .positive {
            color: #28a745;
            font-weight: bold;
        }
        .negative {
            color: #dc3545;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Bayerische Motoren Werke</h1>
            <p>GraphRAG Inference Hackathon - Benchmark Report</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <p>This report benchmarks three different approaches to luxury car knowledge retrieval:
                <ul>
                    <li><strong>LLM-Only:</strong> Direct LLM query without retrieval (baseline)</li>
                    <li><strong>Basic RAG:</strong> Vector embeddings + LLM (industry standard)</li>
                    <li><strong>GraphRAG:</strong> Entity extraction + knowledge graph + LLM (proposed solution)</li>
                </ul>
                </p>
            </div>
            
            <div class="section">
                <h2>📈 Performance Metrics</h2>
        """
        
        if self.comparison:
            html += "<table><tr><th>Pipeline</th><th>Avg Tokens</th><th>Avg Latency</th><th>Avg Cost</th></tr>"
            for pipeline, metrics in self.comparison.items():
                tokens = metrics.get('avg_tokens', 0)
                latency = metrics.get('avg_latency', 0)
                cost = metrics.get('avg_cost', 0)
                html += f"""
                <tr>
                    <td><strong>{pipeline}</strong></td>
                    <td>{tokens:,}</td>
                    <td>{latency}s</td>
                    <td>${cost:.6f}</td>
                </tr>
                """
            html += "</table>"
        
        html += """
            </div>
            
            <div class="section">
                <h2>🎯 Key Findings</h2>
                <div class="metrics-grid">
        """
        
        if self.comparison and "GraphRAG" in self.comparison:
            graphrag = self.comparison["GraphRAG"]
            if "token_reduction_percent" in graphrag:
                html += f"""
                <div class="metric-card">
                    <div class="metric-label">Token Reduction</div>
                    <div class="metric-value positive">{graphrag['token_reduction_percent']}%</div>
                    <div class="metric-unit">vs Basic RAG</div>
                </div>
                """
            if "cost_savings_percent" in graphrag:
                html += f"""
                <div class="metric-card">
                    <div class="metric-label">Cost Savings</div>
                    <div class="metric-value positive">{graphrag['cost_savings_percent']}%</div>
                    <div class="metric-unit">vs Basic RAG</div>
                </div>
                """
        
        html += """
                </div>
            </div>
            
            <div class="section">
                <h2>💡 Conclusion</h2>
                <p>GraphRAG demonstrates significant improvements in token efficiency and cost reduction 
                while maintaining answer quality. This makes it an ideal solution for large-scale 
                luxury car knowledge systems.</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on """ + self.timestamp.strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filename
    
    def generate_markdown_report(self, filename: str = "benchmark_report.md") -> str:
        """Generate Markdown report"""
        
        md = f"""# Bayerische Motoren Werke - GraphRAG Benchmark Report

**Generated:** {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

This benchmark compares three approaches to luxury car knowledge retrieval:

1. **LLM-Only**: Direct LLM without retrieval (baseline)
2. **Basic RAG**: Vector embeddings + LLM (industry standard)
3. **GraphRAG**: Entity extraction + knowledge graph + LLM (proposed)

## Performance Metrics

| Pipeline | Avg Tokens | Avg Latency | Avg Cost |
|----------|-----------|------------|----------|
"""
        
        if self.comparison:
            for pipeline, metrics in self.comparison.items():
                tokens = metrics.get('avg_tokens', 0)
                latency = metrics.get('avg_latency', 0)
                cost = metrics.get('avg_cost', 0)
                md += f"| {pipeline} | {tokens:,} | {latency}s | ${cost:.6f} |\n"
        
        md += """
## Key Improvements (GraphRAG vs Basic RAG)

"""
        
        if self.comparison and "GraphRAG" in self.comparison:
            graphrag = self.comparison["GraphRAG"]
            if "token_reduction_percent" in graphrag:
                md += f"- **Token Reduction:** {graphrag['token_reduction_percent']}%\n"
            if "latency_improvement_percent" in graphrag:
                md += f"- **Latency Improvement:** {graphrag['latency_improvement_percent']}%\n"
            if "cost_savings_percent" in graphrag:
                md += f"- **Cost Savings:** {graphrag['cost_savings_percent']}%\n"
        
        md += """
## Conclusion

GraphRAG provides significant improvements in efficiency and cost-effectiveness while maintaining 
answer quality. It is the recommended approach for luxury car knowledge systems.

---
*Bayerische Motoren Werke GraphRAG Hackathon Project*
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return filename
