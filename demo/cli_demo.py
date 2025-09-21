import argparse
import yaml
import json
import sys
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.align import Align

from core.fetcher import PRFetcher
from core.analyzer import Analyzer
from core.feedback import FeedbackGenerator
from core.scorer import PRScorer
from utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

def load_config():
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        console.print("[red]Error: config.yml not found[/red]")
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing config.yml: {e}[/red]")
        sys.exit(1)

def print_header():
    """Print application header"""
    header = """
╔══════════════════════════════════════════════════════════════╗
║                    🤖 PR Review Agent                        ║
║              AI-Powered Code Quality Analysis               ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(header, style="bold blue", box=box.DOUBLE))

def print_pr_info(pr_data: Dict[str, Any]):
    """Print PR information"""
    info_table = Table(title="📋 Pull Request Information", box=box.ROUNDED)
    info_table.add_column("Property", style="cyan", no_wrap=True)
    info_table.add_column("Value", style="white")
    
    info_table.add_row("ID", str(pr_data.get("id", "N/A")))
    info_table.add_row("Title", pr_data.get("title", "N/A"))
    info_table.add_row("Author", pr_data.get("author", "N/A"))
    info_table.add_row("State", pr_data.get("state", "N/A"))
    info_table.add_row("Files Changed", str(pr_data.get("changed_files", 0)))
    info_table.add_row("Additions", str(pr_data.get("additions", 0)))
    info_table.add_row("Deletions", str(pr_data.get("deletions", 0)))
    
    console.print(info_table)

def print_score_summary(score_data: Dict[str, Any]):
    """Print score summary with visual indicators"""
    total_score = score_data.get("total_score", 0)
    grade = score_data.get("grade", "F")
    
    # Color based on score
    if total_score >= 90:
        score_color = "green"
        grade_style = "bold green"
    elif total_score >= 80:
        score_color = "yellow"
        grade_style = "bold yellow"
    elif total_score >= 70:
        score_color = "orange"
        grade_style = "bold orange"
    else:
        score_color = "red"
        grade_style = "bold red"
    
    # Score panel
    score_text = f"[{score_color}]{total_score:.1f}/100[/{score_color}]"
    grade_text = f"[{grade_style}]{grade}[/{grade_style}]"
    
    score_panel = Panel(
        f"{score_text}\n{grade_text}",
        title="🎯 Overall Score",
        border_style=score_color
    )
    
    console.print(score_panel)
    
    # Breakdown table
    breakdown_table = Table(title="📊 Score Breakdown", box=box.ROUNDED)
    breakdown_table.add_column("Category", style="cyan")
    breakdown_table.add_column("Score", style="white", justify="right")
    breakdown_table.add_column("Status", style="white", justify="center")
    
    for category, score in score_data.get("breakdown", {}).items():
        status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        breakdown_table.add_row(
            category.title(),
            f"{score:.1f}",
            status
        )
    
    console.print(breakdown_table)

def print_issues_summary(analysis: List[Dict[str, Any]]):
    """Print issues summary"""
    if not analysis:
        console.print(Panel("🎉 No issues found! Excellent code quality!", style="green"))
        return
    
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
    
    # Severity summary
    severity_table = Table(title="🚨 Issues by Severity", box=box.ROUNDED)
    severity_table.add_column("Severity", style="cyan")
    severity_table.add_column("Count", style="white", justify="right")
    severity_table.add_column("Icon", style="white", justify="center")
    
    severity_icons = {
        "error": "🔴",
        "high": "🟠", 
        "medium": "🟡",
        "low": "🟢",
        "info": "🔵"
    }
    
    for severity, count in severity_counts.items():
        if count > 0:
            severity_table.add_row(
                severity.title(),
                str(count),
                severity_icons.get(severity, "⚪")
            )
    
    console.print(severity_table)
    
    # Category summary
    if category_counts:
        category_table = Table(title="📂 Issues by Category", box=box.ROUNDED)
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Count", style="white", justify="right")
        
        for category, count in category_counts.items():
            category_table.add_row(category.title(), str(count))
        
        console.print(category_table)

def print_detailed_feedback(feedback: List[Dict[str, Any]], max_items: int = 20):
    """Print detailed feedback"""
    if not feedback:
        return
    
    console.print(f"\n[bold]📝 Detailed Feedback (showing first {min(max_items, len(feedback))} items):[/bold]")
    
    for i, item in enumerate(feedback[:max_items]):
        severity = item.get("severity", "info")
        file_path = item.get("file", "unknown")
        line = item.get("line", 0)
        message = item.get("message", "No message")
        suggestions = item.get("suggestions", [])
        
        # Color based on severity
        severity_colors = {
            "error": "red",
            "high": "orange",
            "medium": "yellow", 
            "low": "green",
            "info": "blue"
        }
        color = severity_colors.get(severity, "white")
        
        # Create feedback panel
        feedback_text = f"[bold]{file_path}:{line}[/bold]\n"
        feedback_text += f"[{color}]{message}[/{color}]\n"
        
        if suggestions:
            feedback_text += "\n[bold]Suggestions:[/bold]\n"
            for suggestion in suggestions:
                feedback_text += f"• {suggestion}\n"
        
        feedback_panel = Panel(
            feedback_text,
            title=f"[{color}]{severity.upper()}[/{color}] - {item.get('category', 'unknown').title()}",
            border_style=color
        )
        
        console.print(feedback_panel)

def print_recommendations(score_data: Dict[str, Any]):
    """Print recommendations"""
    recommendations = score_data.get("recommendations", [])
    if not recommendations:
        return
    
    console.print("\n[bold]💡 Recommendations:[/bold]")
    
    for i, rec in enumerate(recommendations, 1):
        console.print(f"{i}. {rec}")

def print_metrics(score_data: Dict[str, Any]):
    """Print detailed metrics"""
    metrics = score_data.get("metrics", {})
    if not metrics:
        return
    
    metrics_table = Table(title="📈 Detailed Metrics", box=box.ROUNDED)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="white", justify="right")
    
    metrics_table.add_row("Total Issues", str(metrics.get("total_issues", 0)))
    metrics_table.add_row("Files Affected", str(metrics.get("files_affected", 0)))
    metrics_table.add_row("Lines Affected", str(metrics.get("lines_affected", 0)))
    
    # Issues by severity
    for severity, count in metrics.get("issues_by_severity", {}).items():
        if count > 0:
            metrics_table.add_row(f"{severity.title()} Issues", str(count))
    
    console.print(metrics_table)

def export_results(pr_data: Dict[str, Any], analysis: List[Dict[str, Any]], 
                  feedback: List[Dict[str, Any]], score_data: Dict[str, Any], 
                  output_file: str):
    """Export results to JSON file"""
    export_data = {
        "pr_data": pr_data,
        "analysis": analysis,
        "feedback": feedback,
        "score": score_data,
        "exported_at": "2024-01-01T00:00:00Z",  # Would use datetime.now().isoformat()
        "version": "1.0.0"
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        console.print(f"[green]✅ Results exported to {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered PR Review Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_demo.py --server github --repo octocat/Hello-World --pr-id 1
  python cli_demo.py --server gitlab --repo mygroup/myproject --pr-id 123 --export results.json
  python cli_demo.py --server bitbucket --repo myworkspace/myrepo --pr-id 456 --verbose
        """
    )
    
    parser.add_argument("--server", choices=["github", "gitlab", "bitbucket"], 
                       default="github", help="Git server to use")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--pr-id", type=int, required=True, help="Pull request/Merge request ID")
    parser.add_argument("--export", help="Export results to JSON file")
    parser.add_argument("--max-feedback", type=int, default=20, 
                       help="Maximum number of feedback items to display")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--no-ai", action="store_true", 
                       help="Disable AI-powered feedback")
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Load configuration
    config = load_config()
    config["server"] = args.server
    config["repo"] = args.repo
    config["pr_id"] = args.pr_id
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Step 1: Fetch PR
            task1 = progress.add_task("Fetching pull request...", total=None)
            fetcher = PRFetcher(args.server, config)
            pr_data = fetcher.get_pr(args.repo, args.pr_id)
            progress.update(task1, description="✅ Pull request fetched")
            
            # Step 2: Analyze
            task2 = progress.add_task("Analyzing code changes...", total=None)
            analyzer = Analyzer()
            analysis = analyzer.analyze(pr_data["diffs"])
            progress.update(task2, description="✅ Code analysis completed")
            
            # Step 3: Generate Feedback
            task3 = progress.add_task("Generating feedback...", total=None)
            feedback_generator = FeedbackGenerator(use_ai=not args.no_ai)
            feedback = feedback_generator.generate(analysis)
            progress.update(task3, description="✅ Feedback generated")
            
            # Step 4: Score
            task4 = progress.add_task("Calculating score...", total=None)
            scorer = PRScorer()
            score_data = scorer.score(analysis)
            progress.update(task4, description="✅ Score calculated")
        
        # Print results
        console.print("\n")
        print_pr_info(pr_data)
        print_score_summary(score_data)
        print_issues_summary(analysis)
        print_detailed_feedback(feedback, args.max_feedback)
        print_recommendations(score_data)
        print_metrics(score_data)
        
        # Export if requested
        if args.export:
            export_results(pr_data, analysis, feedback, score_data, args.export)
        
        # Final summary
        total_score = score_data.get("total_score", 0)
        if total_score >= 90:
            console.print("\n[bold green]🎉 Excellent code quality! Ready to merge![/bold green]")
        elif total_score >= 80:
            console.print("\n[bold yellow]⚠️ Good code quality with minor issues to address.[/bold yellow]")
        elif total_score >= 70:
            console.print("\n[bold orange]🔧 Code quality needs improvement before merging.[/bold orange]")
        else:
            console.print("\n[bold red]🚫 Code quality is below standards. Significant improvements needed.[/bold red]")
            
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        if args.verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main()
