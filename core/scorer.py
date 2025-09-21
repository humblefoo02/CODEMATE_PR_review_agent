from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class PRScorer:
    def __init__(self):
        # Scoring weights for different categories
        self.category_weights = {
            'security': 0.3,      # Security issues are most critical
            'error': 0.25,        # Errors are very important
            'complexity': 0.2,    # Complexity affects maintainability
            'style': 0.15,        # Style is important for readability
            'maintainability': 0.1,  # General maintainability
            'maintenance': 0.05,  # TODO/FIXME comments
            'unknown': 0.1        # Unknown issues
        }
        
        # Severity penalties
        self.severity_penalties = {
            'error': 20,
            'high': 15,
            'medium': 10,
            'low': 5,
            'info': 2
        }
        
        # Tool-specific weights
        self.tool_weights = {
            'bandit': 1.5,        # Security tools are critical
            'safety': 1.5,        # Dependency vulnerabilities are critical
            'radon': 1.2,         # Complexity analysis is important
            'flake8': 1.0,        # Standard linting
            'custom': 0.8,        # Custom analysis
            'ai': 1.1             # AI feedback is valuable
        }

    def score(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive scoring system for PR quality
        Returns detailed score breakdown
        """
        if not issues:
            return {
                'total_score': 100,
                'grade': 'A+',
                'breakdown': {
                    'security': 100,
                    'quality': 100,
                    'maintainability': 100,
                    'style': 100
                },
                'summary': 'No issues found - excellent code quality!'
            }
        
        logger.info(f"Scoring {len(issues)} issues")
        
        # Calculate base score
        base_score = 100
        
        # Group issues by category
        issues_by_category = self._group_issues_by_category(issues)
        
        # Calculate category scores
        category_scores = {}
        total_penalty = 0
        
        for category, category_issues in issues_by_category.items():
            category_penalty = self._calculate_category_penalty(category, category_issues)
            category_scores[category] = max(0, 100 - category_penalty)
            total_penalty += category_penalty * self.category_weights.get(category, 0.1)
        
        # Calculate final score
        final_score = max(0, base_score - total_penalty)
        
        # Determine grade
        grade = self._calculate_grade(final_score)
        
        # Generate summary
        summary = self._generate_summary(issues, final_score, category_scores)
        
        # Calculate additional metrics
        metrics = self._calculate_metrics(issues)
        
        return {
            'total_score': round(final_score, 1),
            'grade': grade,
            'breakdown': category_scores,
            'summary': summary,
            'metrics': metrics,
            'recommendations': self._generate_recommendations(issues, category_scores)
        }

    def _group_issues_by_category(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group issues by category"""
        categories = {}
        for issue in issues:
            category = issue.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(issue)
        return categories

    def _calculate_category_penalty(self, category: str, issues: List[Dict[str, Any]]) -> float:
        """Calculate penalty for a specific category"""
        penalty = 0
        
        for issue in issues:
            severity = issue.get('severity', 'info')
            tool = issue.get('tool', 'unknown')
            
            # Base penalty from severity
            base_penalty = self.severity_penalties.get(severity, 5)
            
            # Apply tool weight
            tool_weight = self.tool_weights.get(tool, 1.0)
            
            # Apply category-specific multipliers
            if category == 'security':
                base_penalty *= 1.5
            elif category == 'error':
                base_penalty *= 1.3
            elif category == 'complexity':
                base_penalty *= 1.2
            
            penalty += base_penalty * tool_weight
        
        return penalty

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade based on score"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 55:
            return 'C-'
        elif score >= 50:
            return 'D'
        else:
            return 'F'

    def _generate_summary(self, issues: List[Dict[str, Any]], score: float, category_scores: Dict[str, float]) -> str:
        """Generate human-readable summary"""
        total_issues = len(issues)
        
        # Count issues by severity
        severity_counts = {'error': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for issue in issues:
            severity = issue.get('severity', 'info')
            severity_counts[severity] += 1
        
        # Count issues by category
        category_counts = {}
        for issue in issues:
            category = issue.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Generate summary
        if score >= 90:
            summary = f"Excellent code quality! Score: {score:.1f}/100. "
        elif score >= 80:
            summary = f"Good code quality with minor issues. Score: {score:.1f}/100. "
        elif score >= 70:
            summary = f"Code quality needs improvement. Score: {score:.1f}/100. "
        elif score >= 60:
            summary = f"Code quality is below standards. Score: {score:.1f}/100. "
        else:
            summary = f"Code quality is poor and needs significant improvement. Score: {score:.1f}/100. "
        
        # Add specific issue counts
        if severity_counts['error'] > 0:
            summary += f"Found {severity_counts['error']} errors. "
        if severity_counts['high'] > 0:
            summary += f"Found {severity_counts['high']} high-severity issues. "
        if severity_counts['medium'] > 0:
            summary += f"Found {severity_counts['medium']} medium-severity issues. "
        
        # Add category-specific feedback
        if 'security' in category_counts and category_counts['security'] > 0:
            summary += f"Security issues detected ({category_counts['security']}). "
        if 'complexity' in category_counts and category_counts['complexity'] > 0:
            summary += f"Complexity issues found ({category_counts['complexity']}). "
        
        return summary.strip()

    def _calculate_metrics(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate additional metrics"""
        metrics = {
            'total_issues': len(issues),
            'issues_by_severity': {},
            'issues_by_category': {},
            'issues_by_tool': {},
            'files_affected': set(),
            'lines_affected': set()
        }
        
        for issue in issues:
            # Count by severity
            severity = issue.get('severity', 'info')
            metrics['issues_by_severity'][severity] = metrics['issues_by_severity'].get(severity, 0) + 1
            
            # Count by category
            category = issue.get('category', 'unknown')
            metrics['issues_by_category'][category] = metrics['issues_by_category'].get(category, 0) + 1
            
            # Count by tool
            tool = issue.get('tool', 'unknown')
            metrics['issues_by_tool'][tool] = metrics['issues_by_tool'].get(tool, 0) + 1
            
            # Track affected files and lines
            if issue.get('file'):
                metrics['files_affected'].add(issue['file'])
            if issue.get('line'):
                metrics['lines_affected'].add(issue['line'])
        
        # Convert sets to counts
        metrics['files_affected'] = len(metrics['files_affected'])
        metrics['lines_affected'] = len(metrics['lines_affected'])
        
        return metrics

    def _generate_recommendations(self, issues: List[Dict[str, Any]], category_scores: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Security recommendations
        security_issues = [i for i in issues if i.get('category') == 'security']
        if security_issues:
            recommendations.append("🔒 Address security issues immediately - these are critical for production safety")
        
        # Error recommendations
        error_issues = [i for i in issues if i.get('severity') == 'error']
        if error_issues:
            recommendations.append("❌ Fix all errors before merging - these will cause runtime failures")
        
        # Complexity recommendations
        complexity_issues = [i for i in issues if i.get('category') == 'complexity']
        if complexity_issues:
            recommendations.append("🧩 Refactor complex functions to improve maintainability")
        
        # Style recommendations
        style_issues = [i for i in issues if i.get('category') == 'style']
        if style_issues:
            recommendations.append("📝 Fix style issues to improve code readability")
        
        # General recommendations based on score
        total_issues = len(issues)
        if total_issues > 20:
            recommendations.append("📊 Consider breaking this PR into smaller, more focused changes")
        elif total_issues > 10:
            recommendations.append("🔍 Review the code more carefully before submitting")
        
        # Tool-specific recommendations
        if any(i.get('tool') == 'bandit' for i in issues):
            recommendations.append("🛡️ Run security scans regularly in your development workflow")
        
        if any(i.get('tool') == 'radon' for i in issues):
            recommendations.append("📊 Consider adding complexity checks to your CI/CD pipeline")
        
        return recommendations
