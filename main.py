#!/usr/bin/env python3
"""
PR Review Agent - Main Entry Point
AI-powered pull request analysis and review system
"""

import yaml
import sys
import argparse
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel

from core.fetcher import PRFetcher
from core.analyzer import Analyzer
from core.feedback import FeedbackGenerator
from core.scorer import PRScorer
from utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        console.print("[red]Error: config.yml not found[/red]")
        console.print("Please create a config.yml file with your API keys and settings.")
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing config.yml: {e}[/red]")
        sys.exit(1)

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🤖 PR Review Agent                        ║
    ║              AI-Powered Code Quality Analysis               ║
    ║                                                              ║
    ║  Features:                                                    ║
    ║  • Multi-platform support (GitHub, GitLab, Bitbucket)       ║
    ║  • AI-powered feedback generation                            ║
    ║  • Comprehensive code analysis                               ║
    ║  • Security vulnerability detection                          ║
    ║  • Code quality scoring                                      ║
    ║  • Interactive web dashboard                                ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue", box="double"))

def analyze_pr(server: str, repo: str, pr_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a pull request and return comprehensive results"""
    try:
        console.print(f"[cyan]Fetching PR #{pr_id} from {server}/{repo}[/cyan]")
        
        # Step 1: Fetch PR
        fetcher = PRFetcher(server, config)
        pr_data = fetcher.get_pr(repo, pr_id)
        console.print(f"[green]✅ Fetched PR: {pr_data.get('title', 'No title')}[/green]")
        
        # Step 2: Analyze
        console.print("[cyan]Analyzing code changes...[/cyan]")
        analyzer = Analyzer()
        issues = analyzer.analyze(pr_data["diffs"])
        console.print(f"[green]✅ Found {len(issues)} issues[/green]")
        
        # Step 3: Generate Feedback
        console.print("[cyan]Generating feedback...[/cyan]")
        feedback_generator = FeedbackGenerator()
        feedback = feedback_generator.generate(issues)
        console.print(f"[green]✅ Generated {len(feedback)} feedback items[/green]")
        
        # Step 4: Score
        console.print("[cyan]Calculating score...[/cyan]")
        scorer = PRScorer()
        score_data = scorer.score(issues)
        console.print(f"[green]✅ Score: {score_data.get('total_score', 0):.1f}/100 ({score_data.get('grade', 'F')})[/green]")
        
        return {
            "pr_data": pr_data,
            "analysis": issues,
            "feedback": feedback,
            "score": score_data
        }
        
    except Exception as e:
        console.print(f"[red]❌ Error analyzing PR: {e}[/red]")
        logger.error(f"Error analyzing PR: {e}")
        raise

def print_summary(results: Dict[str, Any]):
    """Print analysis summary"""
    pr_data = results["pr_data"]
    analysis = results["analysis"]
    feedback = results["feedback"]
    score_data = results["score"]
    
    # PR Information
    console.print("\n[bold]📋 Pull Request Information:[/bold]")
    console.print(f"  Title: {pr_data.get('title', 'N/A')}")
    console.print(f"  Author: {pr_data.get('author', 'N/A')}")
    console.print(f"  Files Changed: {pr_data.get('changed_files', 0)}")
    console.print(f"  Additions: {pr_data.get('additions', 0)}")
    console.print(f"  Deletions: {pr_data.get('deletions', 0)}")
    
    # Score Summary
    total_score = score_data.get("total_score", 0)
    grade = score_data.get("grade", "F")
    
    if total_score >= 90:
        score_color = "green"
        status = "🎉 Excellent!"
    elif total_score >= 80:
        score_color = "yellow"
        status = "⚠️ Good with minor issues"
    elif total_score >= 70:
        score_color = "orange"
        status = "🔧 Needs improvement"
    else:
        score_color = "red"
        status = "🚫 Below standards"
    
    console.print(f"\n[bold]🎯 Overall Score: [{score_color}]{total_score:.1f}/100 ({grade})[/{score_color}] - {status}[/bold]")
    
    # Issues Summary
    if analysis:
        console.print(f"\n[bold]🚨 Issues Found: {len(analysis)}[/bold]")
        
        # Count by severity
        severity_counts = {"error": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for issue in analysis:
            severity = issue.get("severity", "info")
            severity_counts[severity] += 1
        
        for severity, count in severity_counts.items():
            if count > 0:
                console.print(f"  {severity.title()}: {count}")
    else:
        console.print("\n[bold green]🎉 No issues found! Excellent code quality![/bold green]")
    
    # Top Recommendations
    recommendations = score_data.get("recommendations", [])
    if recommendations:
        console.print(f"\n[bold]💡 Top Recommendations:[/bold]")
        for i, rec in enumerate(recommendations[:3], 1):
            console.print(f"  {i}. {rec}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI-Powered PR Review Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --server github --repo octocat/Hello-World --pr-id 1
  python main.py --server gitlab --repo mygroup/myproject --pr-id 123
  python main.py --server bitbucket --repo myworkspace/myrepo --pr-id 456

For more advanced features, use:
  python demo/cli_demo.py --help
  python demo/web_demo.py
        """
    )
    
    parser.add_argument("--server", choices=["github", "gitlab", "bitbucket"], 
                       default="github", help="Git server to use")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--pr-id", type=int, required=True, help="Pull request/Merge request ID")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Load configuration
    config = load_config()
    config["server"] = args.server
    config["repo"] = args.repo
    config["pr_id"] = args.pr_id
    
    try:
        # Analyze PR
        results = analyze_pr(args.server, args.repo, args.pr_id, config)
        
        # Print summary
        print_summary(results)
        
        # Final message
        total_score = results["score"].get("total_score", 0)
        if total_score >= 90:
            console.print("\n[bold green]🎉 Ready to merge![/bold green]")
        elif total_score >= 80:
            console.print("\n[bold yellow]⚠️ Address minor issues before merging.[/bold yellow]")
        elif total_score >= 70:
            console.print("\n[bold orange]🔧 Significant improvements needed.[/bold orange]")
        else:
            console.print("\n[bold red]🚫 Major issues must be resolved.[/bold red]")
            
        console.print(f"\n[dim]For detailed analysis, use: python demo/cli_demo.py --server {args.server} --repo {args.repo} --pr-id {args.pr_id}[/dim]")
        console.print(f"[dim]For web interface, use: python demo/web_demo.py[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal error: {e}[/bold red]")
        if args.verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main()
