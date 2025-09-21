import streamlit as st
import yaml
import json
import time
from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.fetcher import PRFetcher
from core.analyzer import Analyzer
from core.feedback import FeedbackGenerator
from core.scorer import PRScorer
from utils.logger import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="🤖 PR Review Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .issue-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-card {
        border-left-color: #51cf66;
    }
    .warning-card {
        border-left-color: #ffd43b;
    }
    .error-card {
        border-left-color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error("❌ config.yml not found. Please create a config.yml file with your API keys.")
        st.stop()
    except yaml.YAMLError as e:
        st.error(f"❌ Error parsing config.yml: {e}")
        st.stop()

def analyze_pr(server: str, repo: str, pr_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a pull request and return comprehensive results"""
    try:
        with st.spinner(f"🔍 Analyzing PR #{pr_id} from {server}/{repo}..."):
            # Step 1: Fetch PR
            fetcher = PRFetcher(server, config)
            pr_data = fetcher.get_pr(repo, pr_id)
            
            # Step 2: Analyze
            analyzer = Analyzer()
            analysis = analyzer.analyze(pr_data["diffs"])
            
            # Step 3: Generate Feedback
            feedback_generator = FeedbackGenerator()
            feedback = feedback_generator.generate(analysis)
            
            # Step 4: Score
            scorer = PRScorer()
            score_data = scorer.score(analysis)
            
            return {
                "pr_data": pr_data,
                "analysis": analysis,
                "feedback": feedback,
                "score": score_data
            }
    except Exception as e:
        st.error(f"❌ Error analyzing PR: {e}")
        return None

def display_pr_info(pr_data: Dict[str, Any]):
    """Display PR information"""
    st.subheader("📋 Pull Request Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("PR ID", pr_data.get("id", "N/A"))
        st.metric("Author", pr_data.get("author", "N/A"))
        st.metric("State", pr_data.get("state", "N/A"))
    
    with col2:
        st.metric("Files Changed", pr_data.get("changed_files", 0))
        st.metric("Additions", pr_data.get("additions", 0))
        st.metric("Deletions", pr_data.get("deletions", 0))
    
    with col3:
        st.metric("Commits", pr_data.get("commits", 0))
        if pr_data.get("created_at"):
            st.metric("Created", pr_data.get("created_at", "N/A"))
        if pr_data.get("updated_at"):
            st.metric("Updated", pr_data.get("updated_at", "N/A"))
    
    # PR Title and Description
    if pr_data.get("title"):
        st.markdown(f"**Title:** {pr_data['title']}")
    if pr_data.get("body"):
        with st.expander("📝 Description"):
            st.markdown(pr_data["body"])

def display_score_summary(score_data: Dict[str, Any]):
    """Display score summary with visual indicators"""
    total_score = score_data.get("total_score", 0)
    grade = score_data.get("grade", "F")
    
    # Color based on score
    if total_score >= 90:
        score_color = "🟢"
        status = "Excellent!"
    elif total_score >= 80:
        score_color = "🟡"
        status = "Good with minor issues"
    elif total_score >= 70:
        score_color = "🟠"
        status = "Needs improvement"
    else:
        score_color = "🔴"
        status = "Below standards"
    
    # Main score display
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="text-align: center; margin: 0;">{score_color} {total_score:.1f}/100</h2>
            <h3 style="text-align: center; margin: 0;">Grade: {grade}</h3>
            <p style="text-align: center; margin: 0;">{status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Score breakdown
    st.subheader("📊 Score Breakdown")
    
    breakdown_data = score_data.get("breakdown", {})
    if breakdown_data:
        # Create a bar chart
        categories = list(breakdown_data.keys())
        scores = list(breakdown_data.values())
        
        fig = px.bar(
            x=categories,
            y=scores,
            title="Score by Category",
            labels={"x": "Category", "y": "Score"},
            color=scores,
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display breakdown table
        breakdown_df = pd.DataFrame([
            {"Category": cat.title(), "Score": f"{score:.1f}", "Status": "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"}
            for cat, score in breakdown_data.items()
        ])
        st.dataframe(breakdown_df, use_container_width=True)

def display_issues_summary(analysis: List[Dict[str, Any]]):
    """Display issues summary"""
    if not analysis:
        st.success("🎉 No issues found! Excellent code quality!")
        return
    
    st.subheader(f"🚨 Issues Found: {len(analysis)}")
    
    # Count issues by severity
    severity_counts = {"error": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    category_counts = {}
    tool_counts = {}
    
    for issue in analysis:
        severity = issue.get("severity", "info")
        category = issue.get("category", "unknown")
        tool = issue.get("tool", "unknown")
        
        severity_counts[severity] += 1
        category_counts[category] = category_counts.get(category, 0) + 1
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
    
    # Display charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Severity pie chart
        severity_data = {k: v for k, v in severity_counts.items() if v > 0}
        if severity_data:
            fig = px.pie(
                values=list(severity_data.values()),
                names=list(severity_data.keys()),
                title="Issues by Severity",
                color_discrete_map={
                    "error": "#ff6b6b",
                    "high": "#ffa726",
                    "medium": "#ffd43b",
                    "low": "#51cf66",
                    "info": "#74c0fc"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category bar chart
        if category_counts:
            fig = px.bar(
                x=list(category_counts.keys()),
                y=list(category_counts.values()),
                title="Issues by Category",
                labels={"x": "Category", "y": "Count"}
            )
            st.plotly_chart(fig, use_container_width=True)

def display_detailed_feedback(feedback: List[Dict[str, Any]], max_items: int = 50):
    """Display detailed feedback"""
    if not feedback:
        return
    
    st.subheader(f"📝 Detailed Feedback (showing first {min(max_items, len(feedback))} items)")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_options = ["All"] + list(set(f.get("severity", "info") for f in feedback))
        severity_filter = st.selectbox("Filter by Severity", severity_options)
    with col2:
        category_options = ["All"] + list(set(f.get("category", "unknown") for f in feedback))
        category_filter = st.selectbox("Filter by Category", category_options)
    with col3:
        tool_options = ["All"] + list(set(f.get("tool", "unknown") for f in feedback))
        tool_filter = st.selectbox("Filter by Tool", tool_options)
    
    # Filter feedback
    filtered_feedback = feedback
    if severity_filter != "All":
        filtered_feedback = [f for f in filtered_feedback if f.get("severity") == severity_filter]
    if category_filter != "All":
        filtered_feedback = [f for f in filtered_feedback if f.get("category") == category_filter]
    if tool_filter != "All":
        filtered_feedback = [f for f in filtered_feedback if f.get("tool") == tool_filter]
    
    # Display feedback items
    for i, item in enumerate(filtered_feedback[:max_items]):
        severity = item.get("severity", "info")
        file_path = item.get("file", "unknown")
        line = item.get("line", 0)
        message = item.get("message", "No message")
        suggestions = item.get("suggestions", [])
        
        # Color based on severity
        card_class = "issue-card"
        if severity == "error":
            card_class += " error-card"
        elif severity == "high":
            card_class += " error-card"
        elif severity == "medium":
            card_class += " warning-card"
        else:
            card_class += " success-card"
        
        # Create feedback card
        feedback_html = f"""
        <div class="{card_class}">
            <h4>{file_path}:{line}</h4>
            <p><strong>{severity.upper()}</strong> - {item.get('category', 'unknown').title()}</p>
            <p>{message}</p>
        """
        
        if suggestions:
            feedback_html += "<p><strong>Suggestions:</strong></p><ul>"
            for suggestion in suggestions:
                feedback_html += f"<li>{suggestion}</li>"
            feedback_html += "</ul>"
        
        feedback_html += "</div>"
        
        st.markdown(feedback_html, unsafe_allow_html=True)

def display_recommendations(score_data: Dict[str, Any]):
    """Display recommendations"""
    recommendations = score_data.get("recommendations", [])
    if not recommendations:
        return
    
    st.subheader("💡 Recommendations")
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

def display_metrics(score_data: Dict[str, Any]):
    """Display detailed metrics"""
    metrics = score_data.get("metrics", {})
    if not metrics:
        return
    
    st.subheader("📈 Detailed Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Issues", metrics.get("total_issues", 0))
    with col2:
        st.metric("Files Affected", metrics.get("files_affected", 0))
    with col3:
        st.metric("Lines Affected", metrics.get("lines_affected", 0))
    with col4:
        st.metric("Tools Used", len(metrics.get("issues_by_tool", {})))
    
    # Issues by severity table
    if metrics.get("issues_by_severity"):
        st.subheader("Issues by Severity")
        severity_df = pd.DataFrame([
            {"Severity": severity.title(), "Count": count}
            for severity, count in metrics["issues_by_severity"].items()
            if count > 0
        ])
        st.dataframe(severity_df, use_container_width=True)

def main():
    """Main Streamlit application"""
    # Header
    st.markdown('<h1 class="main-header">🤖 PR Review Agent</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Code Quality Analysis")
    
    # Load configuration
    config = load_config()
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Server selection
    server = st.sidebar.selectbox(
        "Git Server",
        ["github", "gitlab", "bitbucket"],
        index=0
    )
    
    # Repository input
    repo = st.sidebar.text_input(
        "Repository",
        value=config.get("repo", "owner/repository"),
        help="Format: owner/repository"
    )
    
    # PR ID input
    pr_id = st.sidebar.number_input(
        "PR/MR Number",
        min_value=1,
        value=config.get("pr_id", 1),
        help="Pull request or merge request number"
    )
    
    # Analysis options
    st.sidebar.header("🔧 Analysis Options")
    use_ai = st.sidebar.checkbox("Use AI Feedback", value=True, help="Enable OpenAI-powered suggestions")
    max_feedback = st.sidebar.slider("Max Feedback Items", 10, 100, 50, help="Maximum number of feedback items to display")
    
    # Analyze button
    if st.sidebar.button("🚀 Analyze PR", type="primary"):
        if not repo or "/" not in repo:
            st.error("❌ Please enter a valid repository (owner/repo)")
        else:
            # Store results in session state
            st.session_state.results = analyze_pr(server, repo, pr_id, config)
    
    # Display results if available
    if hasattr(st.session_state, 'results') and st.session_state.results:
        results = st.session_state.results
        
        # Display PR information
        display_pr_info(results["pr_data"])
        
        # Display score summary
        display_score_summary(results["score"])
        
        # Display issues summary
        display_issues_summary(results["analysis"])
        
        # Display detailed feedback
        display_detailed_feedback(results["feedback"], max_feedback)
        
        # Display recommendations
        display_recommendations(results["score"])
        
        # Display metrics
        display_metrics(results["score"])
        
        # Export options
        st.subheader("📥 Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export as JSON"):
                export_data = {
                    "pr_data": results["pr_data"],
                    "analysis": results["analysis"],
                    "feedback": results["feedback"],
                    "score": results["score"],
                    "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "version": "1.0.0"
                }
                
                json_str = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"pr-review-{repo.replace('/', '-')}-{pr_id}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export Summary"):
                summary = f"""
# PR Review Report

**Repository:** {repo}
**PR ID:** {pr_id}
**Score:** {results['score']['total_score']:.1f}/100 ({results['score']['grade']})
**Issues:** {len(results['analysis'])}

## Summary
{results['score']['summary']}

## Top Issues
{chr(10).join([f"- {issue.get('message', 'No message')}" for issue in results['analysis'][:10]])}

## Recommendations
{chr(10).join([f"- {rec}" for rec in results['score']['recommendations']])}
                """
                
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name=f"pr-review-summary-{repo.replace('/', '-')}-{pr_id}.md",
                    mime="text/markdown"
                )
    
    else:
        # Welcome message
        st.info("👈 Configure the analysis parameters in the sidebar and click 'Analyze PR' to get started!")
        
        # Show configuration status
        st.subheader("🔧 Configuration Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if config.get("github", {}).get("token"):
                st.success("✅ GitHub configured")
            else:
                st.warning("⚠️ GitHub token missing")
        
        with col2:
            if config.get("gitlab", {}).get("token"):
                st.success("✅ GitLab configured")
            else:
                st.warning("⚠️ GitLab token missing")
        
        with col3:
            if config.get("bitbucket", {}).get("username"):
                st.success("✅ Bitbucket configured")
            else:
                st.warning("⚠️ Bitbucket credentials missing")

if __name__ == "__main__":
    main()
