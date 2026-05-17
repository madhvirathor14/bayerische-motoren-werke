import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import time
from config import Config
from pipelines import LLMOnlyPipeline, BasicRAGPipeline, GraphRAGPipeline
from pipelines.metrics_tracker import MetricsTracker
from evaluation.accuracy_evaluator import AccuracyEvaluator
from evaluation.benchmark_report import BenchmarkReportGenerator

# Page Config
st.set_page_config(
    page_title="BMW GraphRAG",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main styles */
    .main {
        background: #f8f9fa;
    }
    
    /* Headers */
    h1 {
        color: #667eea !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #667eea !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    /* Pipeline sections */
    .pipeline-section {
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 15px 0;
        background: white;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Success/Error messages */
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        color: #155724;
    }
    
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 15px;
        border-radius: 5px;
        color: #721c24;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        padding: 10px 20px;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'metrics_tracker' not in st.session_state:
    st.session_state.metrics_tracker = MetricsTracker()

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("## 🚗 BMW GraphRAG")
    
    st.title("⚙️ Configuration")
    
    # Check API Keys
    st.subheader("🔑 API Setup")
    
    if not Config.GROQ_API_KEY:
        st.error("❌ GROQ API Key not found in .env")
        st.markdown("""
        **Setup Instructions:**
        1. Get free GROQ API key: https://console.groq.com
        2. Copy to `.env` file: `GROQ_API_KEY=your_key_here`
        3. Restart the app
        """)
    else:
        st.success("✅ GROQ API Key loaded")
    
    st.divider()
    
    # Sample Queries
    st.subheader("📝 Sample Queries")
    sample_queries = [
        "Compare BMW M5 and Ferrari F8 Tributo",
        "What's the acceleration of Lamborghini Aventador?",
        "Which luxury car is fastest?",
        "Tell me about Porsche 911 history",
        "What makes Mercedes-Benz special?",
        "BMW M5 price and features",
        "Ferrari F8 specifications",
        "Lamborghini Huracan vs Aventador"
    ]
    selected_query = st.selectbox("Quick start queries:", sample_queries)
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    enable_caching = st.checkbox("Enable caching", value=Config.ENABLE_CACHING)
    debug_mode = st.checkbox("Debug mode", value=Config.DEBUG_MODE)
    
    st.divider()
    
    # Project Info
    st.subheader("ℹ️ Project Info")
    st.markdown(f"""
    **Project:** {Config.PROJECT_NAME}
    
    **Description:** {Config.PROJECT_DESCRIPTION}
    
    **Model:** {Config.GROQ_MODEL}
    
    **Status:** {len(st.session_state.results)} queries executed
    """)
    # Project Info ke thoda niche (Line 169 ke baad)
    st.divider()
    st.subheader("🚗 Car Gallery")
    import os

    # Image mapping
    car_images = {
        "BMW M5": "./data/images/bmw.jpg",
        "Ferrari F8": "./data/images/ferrari.jpg",
        "Lamborghini": "./data/images/lamborghini.jpg",
        "Porsche 911": "./data/images/porsche.jpg",
        "Mercedes AMG": "./data/images/mercedes.jpg",
        "Rolls-Royce": "./data/images/rolls_royce.jpg",
        "McLaren 720S": "./data/images/mclaren.jpg",
        "Bentley Continental": "./data/images/bentley.jpg",
    }

    # Display images in sidebar
    for name, path in car_images.items():
        if os.path.exists(path):
            st.image(path, caption=name, use_column_width=True)
        else:
            st.warning(f"Missing: {name}") # Agar file nahi mili toh error dikhayega

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.title("🚗 Bayerische Motoren Werke")
st.markdown("### GraphRAG-Powered Luxury Car Knowledge Engine")

st.divider()

# Query Input Section
st.subheader("🔍 Enter Your Query")

col1, col2 = st.columns([4, 1])

with col1:
    user_query = st.text_area(
        "Ask about luxury cars:",
        value=selected_query,
        height=100,
        placeholder="e.g., Compare BMW M5 and Ferrari F8 Tributo..."
    )

with col2:
    st.write("")
    st.write("")
    run_query = st.button("🚀 Execute", )

st.divider()

# Execute Pipelines
if run_query and user_query and Config.GROQ_API_KEY:
    
    st.info("⏳ Running 3 pipelines... This may take 10-20 seconds.")
    
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    results = {}
    
    try:
        # Initialize pipelines
        status_placeholder.info("🔄 Initializing pipelines...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        llm_only = LLMOnlyPipeline()
        basic_rag = BasicRAGPipeline()
        graphrag = GraphRAGPipeline()
        
        # Run pipelines
        pipeline_configs = [
            ("LLM-Only", llm_only, 30),
            ("Basic RAG", basic_rag, 60),
            ("GraphRAG", graphrag, 90)
        ]
        
        for pipeline_name, pipeline, progress_value in pipeline_configs:
            status_placeholder.info(f"🔄 Running {pipeline_name} pipeline...")
            progress_bar.progress(progress_value)
            
            result = pipeline.query(user_query)
            results[pipeline_name.lower().replace(" ", "_")] = result
            st.session_state.metrics_tracker.add_result(result)
            time.sleep(1)
        
        progress_bar.progress(100)
        status_placeholder.success("✅ All pipelines executed successfully!")
        time.sleep(1)
        status_placeholder.empty()
        progress_bar.empty()
        
        # Store in session
        st.session_state.results.append({
            "query": user_query,
            "timestamp": datetime.now().isoformat(),
            "results": results
        })
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()
    
    st.divider()
    
    # Display Results Side-by-Side
    st.subheader("📊 Pipeline Responses")
    
    cols = st.columns(3)
    
    for idx, (pipeline_key, pipeline_name) in enumerate([
        ("llm_only", "LLM-Only"),
        ("basic_rag", "Basic RAG"),
        ("graphrag", "GraphRAG")
    ]):
        with cols[idx]:
            if pipeline_key in results:
                result = results[pipeline_key]
                
                st.markdown(f"### {result['pipeline']}")
                
                # Status
                if result['status'] == 'success':
                    st.success("✅ Success")
                else:
                    st.error("❌ Error")
                
                # Answer preview
                answer_preview = result['answer'][:250] + "..." if len(result['answer']) > 250 else result['answer']
                st.markdown(f"**Answer:**\n{answer_preview}")
                
                st.divider()
                
                # Metrics
                st.metric(
                    "Total Tokens",
                    result['tokens']['total'],
                    f"{result['tokens']['prompt']} + {result['tokens']['completion']}"
                )
                
                st.metric(
                    "Latency",
                    f"{result['latency_seconds']}s"
                )
                
                st.metric(
                    "Est. Cost",
                    f"${result['cost']:.6f}"
                )
                
                if 'retrieved_chunks' in result:
                    st.metric("Chunks Retrieved", result['retrieved_chunks'])
                
                if 'entities_extracted' in result:
                    st.metric("Entities Found", result['entities_extracted'])
                    st.metric("Relationships Found", result['relationships_found'])
    
    st.divider()
    
    # Detailed Metrics Comparison
    st.subheader("📈 Detailed Metrics Analysis")
    
    # Token Comparison
    col1, col2 = st.columns(2)
    
    with col1:
        fig_tokens = go.Figure()
        
        pipelines_list = []
        tokens_list = []
        colors_list = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for idx, (pipeline_key, pipeline_name) in enumerate([
            ("llm_only", "LLM-Only"),
            ("basic_rag", "Basic RAG"),
            ("graphrag", "GraphRAG")
        ]):
            if pipeline_key in results:
                pipelines_list.append(results[pipeline_key]['pipeline'])
                tokens_list.append(results[pipeline_key]['tokens']['total'])
                colors_list.append(colors[idx])
        
        fig_tokens.add_trace(go.Bar(
            x=pipelines_list,
            y=tokens_list,
            text=tokens_list,
            textposition='outside',
            marker=dict(color=colors_list),
            name='Tokens'
        ))
        
        fig_tokens.update_layout(
            title="Token Usage Comparison",
            yaxis_title="Total Tokens",
            xaxis_title="Pipeline",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_tokens, )
    
    with col2:
        fig_latency = go.Figure()
        
        latency_list = []
        for idx, (pipeline_key, pipeline_name) in enumerate([
            ("llm_only", "LLM-Only"),
            ("basic_rag", "Basic RAG"),
            ("graphrag", "GraphRAG")
        ]):
            if pipeline_key in results:
                latency_list.append(results[pipeline_key]['latency_seconds'])
        
        fig_latency.add_trace(go.Bar(
            x=pipelines_list,
            y=latency_list,
            text=[f"{l}s" for l in latency_list],
            textposition='outside',
            marker=dict(color=colors_list),
            name='Latency'
        ))
        
        fig_latency.update_layout(
            title="Response Latency Comparison",
            yaxis_title="Seconds",
            xaxis_title="Pipeline",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_latency, )
    
    # Cost Comparison
    col1, col2 = st.columns(2)
    
    with col1:
        fig_cost = go.Figure()
        
        costs_list = []
        for idx, (pipeline_key, pipeline_name) in enumerate([
            ("llm_only", "LLM-Only"),
            ("basic_rag", "Basic RAG"),
            ("graphrag", "GraphRAG")
        ]):
            if pipeline_key in results:
                costs_list.append(results[pipeline_key]['cost'])
        
        fig_cost.add_trace(go.Bar(
            x=pipelines_list,
            y=costs_list,
            text=[f"${c:.6f}" for c in costs_list],
            textposition='outside',
            marker=dict(color=colors_list),
            name='Cost'
        ))
        
        fig_cost.update_layout(
            title="Cost Per Query Comparison",
            yaxis_title="USD",
            xaxis_title="Pipeline",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_cost, )
    
    with col2:
        # Key Metrics Box
        st.markdown("### 🎯 Key Findings")
        
        basic_rag_tokens = results['basic_rag']['tokens']['total']
        graphrag_tokens = results['graphrag']['tokens']['total']
        
        token_reduction = ((basic_rag_tokens - graphrag_tokens) / basic_rag_tokens * 100) if basic_rag_tokens > 0 else 0
        
        basic_rag_cost = results['basic_rag']['cost']
        graphrag_cost = results['graphrag']['cost']
        cost_savings = ((basic_rag_cost - graphrag_cost) / basic_rag_cost * 100) if basic_rag_cost > 0 else 0
        
        basic_rag_latency = results['basic_rag']['latency_seconds']
        graphrag_latency = results['graphrag']['latency_seconds']
        latency_improvement = ((basic_rag_latency - graphrag_latency) / basic_rag_latency * 100) if basic_rag_latency > 0 else 0
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown(f"""
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; text-align: center;">
                <p style="color: #666; margin: 0;">Token Reduction</p>
                <p style="font-size: 1.8em; font-weight: bold; color: #28a745; margin: 10px 0;">{token_reduction:.1f}%</p>
                <p style="color: #999; margin: 0; font-size: 0.9em;">GraphRAG vs Basic RAG</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown(f"""
            <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; text-align: center;">
                <p style="color: #666; margin: 0;">Cost Savings</p>
                <p style="font-size: 1.8em; font-weight: bold; color: #0c5460; margin: 10px 0;">{cost_savings:.1f}%</p>
                <p style="color: #999; margin: 0; font-size: 0.9em;">GraphRAG vs Basic RAG</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c:
            st.markdown(f"""
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; text-align: center;">
                <p style="color: #666; margin: 0;">Latency Improvement</p>
                <p style="font-size: 1.8em; font-weight: bold; color: #856404; margin: 10px 0;">{latency_improvement:.1f}%</p>
                <p style="color: #999; margin: 0; font-size: 0.9em;">GraphRAG vs Basic RAG</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# BENCHMARK SECTION
# ============================================================================

st.divider()

st.subheader("📊 Benchmark Summary")

if st.session_state.results:
    col1, col2 = st.columns(2)
    
    with col1:
        comparison = st.session_state.metrics_tracker.calculate_comparison()
        
        st.write("### Overall Metrics")
        
        if comparison:
            for pipeline, metrics in comparison.items():
                st.markdown(f"""
                **{pipeline}**
                - Avg Tokens: {metrics['avg_tokens']:,}
                - Avg Latency: {metrics['avg_latency']}s
                - Avg Cost: ${metrics['avg_cost']:.6f}
                - Queries: {metrics['total_queries']}
                """)
    
    with col2:
        st.write("### Improvements (GraphRAG vs Basic RAG)")
        
        if comparison and "GraphRAG" in comparison:
            graphrag = comparison["GraphRAG"]
            
            improvements = []
            if "token_reduction_percent" in graphrag:
                improvements.append(f"🎯 Tokens: {graphrag['token_reduction_percent']}%")
            if "latency_improvement_percent" in graphrag:
                improvements.append(f"⚡ Latency: {graphrag['latency_improvement_percent']}%")
            if "cost_savings_percent" in graphrag:
                improvements.append(f"💰 Cost: {graphrag['cost_savings_percent']}%")
            
            for imp in improvements:
                st.markdown(f"- {imp}")

# ============================================================================
# FULL ANSWER VIEWER
# ============================================================================

if st.session_state.results:
    st.divider()
    
    st.subheader("📝 Full Answers")
    
    latest_result = st.session_state.results[-1]['results']
    
    tabs = st.tabs(["LLM-Only", "Basic RAG", "GraphRAG"])
    
    for idx, (tab, key) in enumerate(zip(tabs, ["llm_only", "basic_rag", "graphrag"])):
        with tab:
            if key in latest_result:
                result = latest_result[key]
                st.markdown(result['answer'])

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export Results as JSON"):
        st.session_state.metrics_tracker.export_json("benchmark_results.json")
        st.success("✅ Results exported to benchmark_results.json")

with col2:
    if st.button("📊 Generate HTML Report"):
        comparison = st.session_state.metrics_tracker.calculate_comparison()
        report_gen = BenchmarkReportGenerator(st.session_state.results, comparison)
        report_gen.generate_html_report("benchmark_report.html")
        st.success("✅ HTML report generated as benchmark_report.html")

with col3:
    if st.button("🔄 Clear Results"):
        st.session_state.results = []
        st.session_state.metrics_tracker = MetricsTracker()
        st.rerun()

st.markdown("---")

st.markdown("""
<div style="text-align: center; color: #666; margin-top: 20px;">
    <p>🚗 Bayerische Motoren Werke - GraphRAG Inference Hackathon</p>
    <p style="font-size: 0.9em;">Token Reduction | Cost Efficiency | Answer Quality</p>
</div>
""", unsafe_allow_html=True)
