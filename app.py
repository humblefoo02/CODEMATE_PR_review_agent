import streamlit as st
import yaml
import json
import time
from typing import Dict, Any, List

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
</style>
""", unsafe_allow_html=True)

def load_config():
    """Load configuration with hardcoded GitHub token"""
    # Hardcoded configuration for immediate deployment
    config = {
        "server": "github",
        "repo": "octocat/Hello-World",
        "pr_id": 1,
        "github": {
            "token": "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"
        },
        "gitlab": {
            "url": "https://gitlab.com",
            "token": "your_gitlab_token_here"
        },
        "bitbucket": {
            "username": "your_username",
            "password": "your_password"
        }
    }
    
    # Try to load from config.yml if it exists, otherwise use hardcoded config
    try:
        with open("config.yml", "r") as f:
            file_config = yaml.safe_load(f)
            # Merge file config with hardcoded config (file takes precedence)
            if file_config:
                config.update(file_config)
    except (FileNotFoundError, yaml.YAMLError):
        # Use hardcoded config if file doesn't exist or has errors
        pass
    
    return config

def main():
    """Main Streamlit application"""
    # Header
    st.markdown('<h1 class="main-header">🤖 PR Review Agent</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Code Quality Analysis")
    
    # Load configuration
    config = load_config()
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # PR Link input
    st.sidebar.subheader("🔗 Quick Analysis")
    pr_link = st.sidebar.text_input(
        "PR/MR Link",
        placeholder="https://github.com/owner/repo/pull/123",
        help="Paste a GitHub, GitLab, or Bitbucket PR/MR link to auto-fill repository and PR number"
    )
    
    # Show examples
    with st.sidebar.expander("📝 Link Examples"):
        st.markdown("""
        **GitHub:**
        ```
        https://github.com/octocat/Hello-World/pull/1
        ```
        
        **GitLab:**
        ```
        https://gitlab.com/group/project/-/merge_requests/123
        ```
        
        **Bitbucket:**
        ```
        https://bitbucket.org/workspace/repo/pull-requests/456
        ```
        """)
    
    # Auto-extract from link
    extracted_repo = None
    extracted_pr_id = None
    detected_server = "github"
    
    if pr_link:
        try:
            import re
            
            # GitHub PR link
            if "github.com" in pr_link:
                match = re.search(r'github\.com/([^/]+/[^/]+)/pull/(\d+)', pr_link)
                if match:
                    extracted_repo = match.group(1)
                    extracted_pr_id = int(match.group(2))
                    detected_server = "github"
                    st.sidebar.success(f"✅ GitHub: {extracted_repo} PR #{extracted_pr_id}")
                else:
                    st.sidebar.error("❌ Invalid GitHub PR link format")
            
            # GitLab MR link
            elif "gitlab.com" in pr_link or "gitlab" in pr_link:
                match = re.search(r'gitlab\.com/([^/]+/[^/]+)/-/merge_requests/(\d+)', pr_link)
                if match:
                    extracted_repo = match.group(1)
                    extracted_pr_id = int(match.group(2))
                    detected_server = "gitlab"
                    st.sidebar.success(f"✅ GitLab: {extracted_repo} MR !{extracted_pr_id}")
                else:
                    st.sidebar.error("❌ Invalid GitLab MR link format")
            
            # Bitbucket PR link
            elif "bitbucket.org" in pr_link or "bitbucket" in pr_link:
                match = re.search(r'bitbucket\.org/([^/]+/[^/]+)/pull-requests/(\d+)', pr_link)
                if match:
                    extracted_repo = match.group(1)
                    extracted_pr_id = int(match.group(2))
                    detected_server = "bitbucket"
                    st.sidebar.success(f"✅ Bitbucket: {extracted_repo} PR #{extracted_pr_id}")
                else:
                    st.sidebar.error("❌ Invalid Bitbucket PR link format")
            
            else:
                st.sidebar.warning("⚠️ Unsupported link format. Supported: GitHub, GitLab, Bitbucket")
                
        except Exception as e:
            st.sidebar.error(f"❌ Error parsing link: {e}")
            extracted_repo = None
            extracted_pr_id = None
    
    # Server selection
    server_options = ["github", "gitlab", "bitbucket"]
    default_index = server_options.index(detected_server) if detected_server in server_options else 0
    
    server = st.sidebar.selectbox(
        "Git Server",
        server_options,
        index=default_index
    )
    
    # Repository input
    repo = st.sidebar.text_input(
        "Repository",
        value=extracted_repo if extracted_repo else config.get("repo", "owner/repository"),
        help="Format: owner/repository"
    )
    
    # PR ID input
    pr_id = st.sidebar.number_input(
        "PR/MR Number",
        min_value=1,
        value=extracted_pr_id if extracted_pr_id else config.get("pr_id", 1),
        help="Pull request or merge request number"
    )
    
    # Analysis options
    st.sidebar.header("🔧 Analysis Options")
    use_ai = st.sidebar.checkbox("Use AI Feedback", value=True, help="Enable OpenAI-powered suggestions")
    max_feedback = st.sidebar.slider("Max Feedback Items", 10, 100, 50, help="Maximum number of feedback items to display")
    
    # Quick analyze button (appears when link is detected)
    if extracted_repo and extracted_pr_id:
        if st.sidebar.button("⚡ Quick Analyze", type="primary"):
            # Auto-fill the form and analyze
            st.session_state.auto_analyze = True
    
    # Regular analyze button
    if st.sidebar.button("🚀 Analyze PR", type="primary") or st.session_state.get("auto_analyze", False):
        if st.session_state.get("auto_analyze", False):
            st.session_state.auto_analyze = False  # Reset the flag
        
        if not repo or "/" not in repo:
            st.error("❌ Please enter a valid repository (owner/repo)")
        else:
            # Show analysis in progress
            with st.spinner(f"🔍 Analyzing PR #{pr_id} from {server}/{repo}..."):
                try:
                    # Import here to avoid issues if modules are missing
                    from core.fetcher import PRFetcher
                    from core.analyzer import Analyzer
                    from core.feedback import FeedbackGenerator
                    from core.scorer import PRScorer
                    
                    # Step 1: Fetch PR
                    fetcher = PRFetcher(server, config)
                    pr_data = fetcher.get_pr(repo, pr_id)
                    
                    # Step 2: Analyze
                    analyzer = Analyzer()
                    analysis = analyzer.analyze(pr_data["diffs"])
                    
                    # Step 3: Generate Feedback
                    feedback_generator = FeedbackGenerator(use_ai=use_ai)
                    feedback = feedback_generator.generate(analysis)
                    
                    # Step 4: Score
                    scorer = PRScorer()
                    score_data = scorer.score(analysis)
                    
                    # Store results in session state
                    st.session_state.results = {
                        "pr_data": pr_data,
                        "analysis": analysis,
                        "feedback": feedback,
                        "score": score_data
                    }
                    
                    st.success("✅ Analysis completed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {e}")
                    st.info("💡 Make sure your API keys are configured in config.yml")
    
    # Display results if available
    if hasattr(st.session_state, 'results') and st.session_state.results:
        results = st.session_state.results
        
        # Display PR information
        st.subheader("📋 Pull Request Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("PR ID", results["pr_data"].get("id", "N/A"))
            st.metric("Author", results["pr_data"].get("author", "N/A"))
            st.metric("State", results["pr_data"].get("state", "N/A"))
        
        with col2:
            st.metric("Files Changed", results["pr_data"].get("changed_files", 0))
            st.metric("Additions", results["pr_data"].get("additions", 0))
            st.metric("Deletions", results["pr_data"].get("deletions", 0))
        
        with col3:
            st.metric("Commits", results["pr_data"].get("commits", 0))
            if results["pr_data"].get("created_at"):
                st.metric("Created", results["pr_data"].get("created_at", "N/A"))
            if results["pr_data"].get("updated_at"):
                st.metric("Updated", results["pr_data"].get("updated_at", "N/A"))
        
        # PR Title and Description
        if results["pr_data"].get("title"):
            st.markdown(f"**Title:** {results['pr_data']['title']}")
        if results["pr_data"].get("body"):
            with st.expander("📝 Description"):
                st.markdown(results["pr_data"]["body"])
        
        # Score Summary
        st.subheader("🎯 Score Summary")
        
        total_score = results["score"].get("total_score", 0)
        grade = results["score"].get("grade", "F")
        
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
        
        # Issues Summary
        st.subheader(f"🚨 Issues Found: {len(results['analysis'])}")
        
        if results["analysis"]:
            # Count issues by severity
            severity_counts = {"error": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
            for issue in results["analysis"]:
                severity = issue.get("severity", "info")
                severity_counts[severity] += 1
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Error", severity_counts["error"])
            with col2:
                st.metric("High", severity_counts["high"])
            with col3:
                st.metric("Medium", severity_counts["medium"])
            with col4:
                st.metric("Low", severity_counts["low"])
            with col5:
                st.metric("Info", severity_counts["info"])
        else:
            st.success("🎉 No issues found! Excellent code quality!")
        
        # Detailed Feedback
        if results["feedback"]:
            st.subheader(f"📝 Detailed Feedback (showing first {min(max_feedback, len(results['feedback']))} items)")
            
            for i, item in enumerate(results["feedback"][:max_feedback]):
                severity = item.get("severity", "info")
                file_path = item.get("file", "unknown")
                line = item.get("line", 0)
                message = item.get("message", "No message")
                suggestions = item.get("suggestions", [])
                
                # Color based on severity
                if severity == "error":
                    st.error(f"**{file_path}:{line}** - {message}")
                elif severity == "high":
                    st.error(f"**{file_path}:{line}** - {message}")
                elif severity == "medium":
                    st.warning(f"**{file_path}:{line}** - {message}")
                else:
                    st.info(f"**{file_path}:{line}** - {message}")
                
                if suggestions:
                    with st.expander("💡 Suggestions"):
                        for suggestion in suggestions:
                            st.write(f"• {suggestion}")
        
        # Recommendations
        recommendations = results["score"].get("recommendations", [])
        if recommendations:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        
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
    
    else:
        # Welcome message
        if pr_link and extracted_repo and extracted_pr_id:
            st.success(f"🔗 Ready to analyze: **{extracted_repo}** PR #{extracted_pr_id}")
            st.info("👈 Click '⚡ Quick Analyze' in the sidebar to start analysis!")
        else:
            st.info("👈 Paste a PR/MR link in the sidebar or configure manually to get started!")
        
        # Show current analysis target
        if repo and pr_id:
            st.subheader("🎯 Analysis Target")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Server", server.title())
            with col2:
                st.metric("Repository", repo)
            with col3:
                st.metric("PR/MR Number", pr_id)
        
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
        
        # Show link examples
        st.subheader("🔗 Supported Link Formats")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **GitHub:**
            ```
            https://github.com/
            owner/repo/pull/123
            ```
            """)
        
        with col2:
            st.markdown("""
            **GitLab:**
            ```
            https://gitlab.com/
            group/project/-/merge_requests/123
            ```
            """)
        
        with col3:
            st.markdown("""
            **Bitbucket:**
            ```
            https://bitbucket.org/
            workspace/repo/pull-requests/456
            ```
            """)

if __name__ == "__main__":
    main()
