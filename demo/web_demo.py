from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import yaml
import os
from typing import Dict, Any, List
import json
from datetime import datetime

from core.fetcher import PRFetcher
from core.analyzer import Analyzer
from core.feedback import FeedbackGenerator
from core.scorer import PRScorer
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="PR Review Agent",
    description="AI-powered Pull Request Review System",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="demo/templates")

# Global variables for demo
current_pr_data = None
current_analysis = None
current_feedback = None
current_score = None

def load_config():
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config.yml not found")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config.yml: {e}")
        return {}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "PR Review Agent Dashboard"
    })

@app.get("/api/analyze")
async def analyze_pr(server: str, repo: str, pr_id: int):
    """Analyze a pull request"""
    global current_pr_data, current_analysis, current_feedback, current_score
    
    try:
        config = load_config()
        if not config:
            raise HTTPException(status_code=500, detail="Configuration not found")
        
        # Update config with provided parameters
        config["server"] = server
        config["repo"] = repo
        config["pr_id"] = pr_id
        
        logger.info(f"Analyzing PR #{pr_id} from {server}/{repo}")
        
        # Step 1: Fetch PR
        fetcher = PRFetcher(server, config)
        current_pr_data = fetcher.get_pr(repo, pr_id)
        
        # Step 2: Analyze
        analyzer = Analyzer()
        current_analysis = analyzer.analyze(current_pr_data["diffs"])
        
        # Step 3: Generate Feedback
        feedback_generator = FeedbackGenerator()
        current_feedback = feedback_generator.generate(current_analysis)
        
        # Step 4: Score
        scorer = PRScorer()
        current_score = scorer.score(current_analysis)
        
        return {
            "success": True,
            "pr_data": current_pr_data,
            "analysis": current_analysis,
            "feedback": current_feedback,
            "score": current_score,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing PR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get current analysis status"""
    return {
        "has_pr_data": current_pr_data is not None,
        "has_analysis": current_analysis is not None,
        "has_feedback": current_feedback is not None,
        "has_score": current_score is not None,
        "pr_id": current_pr_data.get("id") if current_pr_data else None,
        "total_issues": len(current_analysis) if current_analysis else 0,
        "score": current_score.get("total_score") if current_score else None
    }

@app.get("/api/feedback")
async def get_feedback():
    """Get detailed feedback"""
    if not current_feedback:
        raise HTTPException(status_code=404, detail="No feedback available")
    
    return {
        "feedback": current_feedback,
        "total_items": len(current_feedback)
    }

@app.get("/api/score")
async def get_score():
    """Get detailed score breakdown"""
    if not current_score:
        raise HTTPException(status_code=404, detail="No score available")
    
    return current_score

@app.get("/api/issues")
async def get_issues():
    """Get detailed issues breakdown"""
    if not current_analysis:
        raise HTTPException(status_code=404, detail="No analysis available")
    
    # Group issues by category
    issues_by_category = {}
    for issue in current_analysis:
        category = issue.get('category', 'unknown')
        if category not in issues_by_category:
            issues_by_category[category] = []
        issues_by_category[category].append(issue)
    
    return {
        "issues": current_analysis,
        "by_category": issues_by_category,
        "total_issues": len(current_analysis)
    }

@app.post("/api/comment")
async def create_comment(
    file_path: str = Form(...),
    line: int = Form(...),
    comment: str = Form(...)
):
    """Create a review comment"""
    if not current_pr_data:
        raise HTTPException(status_code=404, detail="No PR data available")
    
    try:
        config = load_config()
        server = config.get("server", "github")
        repo = config.get("repo", "")
        
        fetcher = PRFetcher(server, config)
        
        # Create comment using the appropriate integration
        if hasattr(fetcher.client, 'create_review_comment'):
            success = fetcher.client.create_review_comment(
                repo, 
                current_pr_data["id"], 
                file_path, 
                line, 
                comment
            )
            
            if success:
                return {"success": True, "message": "Comment created successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to create comment")
        else:
            raise HTTPException(status_code=501, detail="Comment creation not supported for this server")
            
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export")
async def export_report(format: str = "json"):
    """Export analysis report"""
    if not current_pr_data or not current_analysis or not current_feedback or not current_score:
        raise HTTPException(status_code=404, detail="No analysis data available")
    
    report = {
        "pr_data": current_pr_data,
        "analysis": current_analysis,
        "feedback": current_feedback,
        "score": current_score,
        "exported_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    
    if format == "json":
        return JSONResponse(content=report)
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
