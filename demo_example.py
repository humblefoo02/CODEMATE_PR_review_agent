#!/usr/bin/env python3
"""
Demo script showing how to use the PR Review Agent
"""

import yaml
import json
from core.fetcher import PRFetcher
from core.analyzer import Analyzer
from core.feedback import FeedbackGenerator
from core.scorer import PRScorer

def load_config():
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yml not found. Please create one with your API keys.")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error parsing config.yml: {e}")
        return None

def demo_analysis():
    """Demonstrate the PR analysis system"""
    print("🤖 PR Review Agent Demo")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Example configuration
    server = "github"
    repo = "octocat/Hello-World"
    pr_id = 1
    
    print(f"📋 Analyzing PR #{pr_id} from {server}/{repo}")
    print()
    
    try:
        # Step 1: Fetch PR
        print("🔍 Fetching pull request...")
        fetcher = PRFetcher(server, config)
        pr_data = fetcher.get_pr(repo, pr_id)
        print(f"✅ Fetched: {pr_data.get('title', 'No title')}")
        print(f"   Files: {pr_data.get('changed_files', 0)}")
        print(f"   Additions: {pr_data.get('additions', 0)}")
        print(f"   Deletions: {pr_data.get('deletions', 0)}")
        print()
        
        # Step 2: Analyze
        print("🔬 Analyzing code changes...")
        analyzer = Analyzer()
        analysis = analyzer.analyze(pr_data["diffs"])
        print(f"✅ Found {len(analysis)} issues")
        
        # Show issue breakdown
        if analysis:
            severity_counts = {}
            for issue in analysis:
                severity = issue.get("severity", "info")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print("   Issues by severity:")
            for severity, count in severity_counts.items():
                print(f"   - {severity}: {count}")
        print()
        
        # Step 3: Generate Feedback
        print("💬 Generating feedback...")
        feedback_generator = FeedbackGenerator()
        feedback = feedback_generator.generate(analysis)
        print(f"✅ Generated {len(feedback)} feedback items")
        print()
        
        # Step 4: Score
        print("📊 Calculating score...")
        scorer = PRScorer()
        score_data = scorer.score(analysis)
        total_score = score_data.get("total_score", 0)
        grade = score_data.get("grade", "F")
        print(f"✅ Score: {total_score:.1f}/100 ({grade})")
        
        # Show score breakdown
        breakdown = score_data.get("breakdown", {})
        if breakdown:
            print("   Score breakdown:")
            for category, score in breakdown.items():
                print(f"   - {category}: {score:.1f}")
        print()
        
        # Show recommendations
        recommendations = score_data.get("recommendations", [])
        if recommendations:
            print("💡 Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
            print()
        
        # Show top issues
        if analysis:
            print("🚨 Top Issues:")
            for i, issue in enumerate(analysis[:5], 1):
                file_path = issue.get("file", "unknown")
                line = issue.get("line", 0)
                message = issue.get("message", "No message")
                severity = issue.get("severity", "info")
                print(f"   {i}. [{severity.upper()}] {file_path}:{line} - {message}")
            print()
        
        # Final assessment
        if total_score >= 90:
            print("🎉 Excellent code quality! Ready to merge!")
        elif total_score >= 80:
            print("⚠️ Good code quality with minor issues to address.")
        elif total_score >= 70:
            print("🔧 Code quality needs improvement before merging.")
        else:
            print("🚫 Code quality is below standards. Significant improvements needed.")
        
        # Export results
        export_data = {
            "pr_data": pr_data,
            "analysis": analysis,
            "feedback": feedback,
            "score": score_data,
            "exported_at": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
        
        with open("demo_results.json", "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        print(f"\n📄 Results exported to demo_results.json")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("💡 Make sure your API keys are configured in config.yml")

def show_usage_examples():
    """Show usage examples"""
    print("\n📚 Usage Examples:")
    print("=" * 50)
    
    print("\n1. Command Line Interface:")
    print("   python main.py --server github --repo owner/repo --pr-id 123")
    
    print("\n2. Advanced CLI with Rich Output:")
    print("   python demo/cli_demo.py --server github --repo owner/repo --pr-id 123 --export results.json")
    
    print("\n3. Streamlit Web Dashboard:")
    print("   python run_streamlit.py")
    print("   # Then open http://localhost:8501")
    
    print("\n4. Docker Deployment:")
    print("   docker-compose up -d")
    print("   # Then open http://localhost:8501")
    
    print("\n5. Programmatic Usage:")
    print("   from core.fetcher import PRFetcher")
    print("   from core.analyzer import Analyzer")
    print("   # ... (see demo_analysis() function)")

if __name__ == "__main__":
    demo_analysis()
    show_usage_examples()
