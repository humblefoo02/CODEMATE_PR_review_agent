import os
from typing import List, Dict, Any
from utils.logger import get_logger
from utils.ai_helpers import AIHelper

logger = get_logger(__name__)

class FeedbackGenerator:
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai and os.getenv('OPENAI_API_KEY')
        self.ai_helper = AIHelper() if self.use_ai else None
        
        # Feedback templates for different issue types
        self.templates = {
            'style': {
                'E501': "Line too long ({length} characters). Consider breaking it into multiple lines or using line continuation.",
                'E302': "Expected 2 blank lines before class definition.",
                'E305': "Expected 2 blank lines after class or function definition.",
                'W293': "Blank line contains whitespace. Remove trailing whitespace.",
                'E111': "Indentation is not a multiple of four spaces.",
                'E112': "Expected an indented block."
            },
            'error': {
                'F841': "Variable '{var_name}' is assigned but never used. Consider removing it or using it.",
                'F401': "Module '{module}' imported but unused. Remove the import if not needed.",
                'F821': "Undefined name '{name}'. Check for typos or missing imports.",
                'F823': "Local variable '{var_name}' referenced before assignment."
            },
            'security': {
                'B101': "Use of hardcoded password detected. Use environment variables or secure configuration.",
                'B102': "Use of exec() detected. This can be dangerous if user input is involved.",
                'B301': "Use of pickle module detected. This can be unsafe for untrusted data.",
                'B302': "Use of marshal module detected. This can be unsafe for untrusted data."
            },
            'complexity': {
                'high_complexity': "Function '{function}' has high cyclomatic complexity ({complexity}). Consider breaking it into smaller functions.",
                'large_function': "Function '{function}' is too large ({lines} lines). Consider refactoring into smaller functions."
            }
        }

    def generate(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate comprehensive feedback from analysis issues
        """
        feedback_items = []
        
        # Group issues by file for better organization
        issues_by_file = {}
        for issue in issues:
            file_path = issue.get('file', 'unknown')
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        for file_path, file_issues in issues_by_file.items():
            logger.info(f"Generating feedback for {file_path} ({len(file_issues)} issues)")
            
            # Generate AI-powered feedback if available
            if self.use_ai and self.ai_helper:
                try:
                    ai_feedback = self.ai_helper.generate_feedback(file_path, file_issues)
                    feedback_items.extend(ai_feedback)
                except Exception as e:
                    logger.error(f"AI feedback generation failed: {e}")
                    # Fall back to template-based feedback
                    feedback_items.extend(self._generate_template_feedback(file_issues))
            else:
                # Use template-based feedback
                feedback_items.extend(self._generate_template_feedback(file_issues))
        
        return self._prioritize_feedback(feedback_items)

    def _generate_template_feedback(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate feedback using predefined templates"""
        feedback_items = []
        
        for issue in issues:
            category = issue.get('category', 'unknown')
            severity = issue.get('severity', 'info')
            tool = issue.get('tool', 'unknown')
            
            # Generate specific feedback based on issue type
            if tool == 'flake8':
                feedback = self._generate_flake8_feedback(issue)
            elif tool == 'bandit':
                feedback = self._generate_security_feedback(issue)
            elif tool == 'radon':
                feedback = self._generate_complexity_feedback(issue)
            elif tool == 'custom':
                feedback = self._generate_custom_feedback(issue)
            else:
                feedback = self._generate_generic_feedback(issue)
            
            feedback_items.append(feedback)
        
        return feedback_items

    def _generate_flake8_feedback(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific feedback for flake8 issues"""
        code = issue.get('code', '')
        message = issue.get('message', '')
        line = issue.get('line', 0)
        
        # Get template message
        template_msg = self.templates.get('style', {}).get(code, message)
        
        # Add specific suggestions
        suggestions = []
        if code == 'E501':
            suggestions.append("Break long lines using parentheses, backslashes, or string concatenation")
        elif code == 'F841':
            suggestions.append("Remove unused variable or use it in your code")
        elif code == 'F401':
            suggestions.append("Remove unused import or use the imported module")
        
        return {
            'file': issue.get('file', ''),
            'line': line,
            'severity': issue.get('severity', 'info'),
            'category': 'style',
            'message': template_msg,
            'suggestions': suggestions,
            'code': code,
            'tool': 'flake8'
        }

    def _generate_security_feedback(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for security issues"""
        message = issue.get('message', '')
        test_id = issue.get('test_id', '')
        confidence = issue.get('confidence', 'medium')
        
        # Security-specific suggestions
        suggestions = []
        if 'hardcoded' in message.lower():
            suggestions.append("Use environment variables or secure configuration management")
            suggestions.append("Consider using a secrets management service")
        elif 'exec' in message.lower():
            suggestions.append("Avoid using exec() with user input")
            suggestions.append("Consider using safer alternatives like ast.literal_eval()")
        
        return {
            'file': issue.get('file', ''),
            'line': issue.get('line', 0),
            'severity': issue.get('severity', 'high'),
            'category': 'security',
            'message': f"Security issue: {message}",
            'suggestions': suggestions,
            'test_id': test_id,
            'confidence': confidence,
            'tool': 'bandit'
        }

    def _generate_complexity_feedback(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for complexity issues"""
        complexity = issue.get('complexity', 0)
        function = issue.get('function', 'unknown')
        
        suggestions = [
            "Break the function into smaller, single-purpose functions",
            "Extract complex logic into separate methods",
            "Consider using design patterns like Strategy or Command",
            "Add early returns to reduce nesting"
        ]
        
        return {
            'file': issue.get('file', ''),
            'line': issue.get('line', 0),
            'severity': issue.get('severity', 'medium'),
            'category': 'complexity',
            'message': f"High complexity in {function} ({complexity})",
            'suggestions': suggestions,
            'complexity': complexity,
            'tool': 'radon'
        }

    def _generate_custom_feedback(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for custom analysis issues"""
        category = issue.get('category', 'unknown')
        message = issue.get('message', '')
        
        suggestions = []
        if category == 'security':
            suggestions.append("Review the code for potential security vulnerabilities")
            suggestions.append("Consider using secure coding practices")
        elif category == 'maintenance':
            suggestions.append("Address TODO/FIXME comments before merging")
            suggestions.append("Consider creating issues for future improvements")
        
        return {
            'file': issue.get('file', ''),
            'line': issue.get('line', 0),
            'severity': issue.get('severity', 'low'),
            'category': category,
            'message': message,
            'suggestions': suggestions,
            'tool': 'custom'
        }

    def _generate_generic_feedback(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic feedback for unknown issue types"""
        return {
            'file': issue.get('file', ''),
            'line': issue.get('line', 0),
            'severity': issue.get('severity', 'info'),
            'category': issue.get('category', 'unknown'),
            'message': issue.get('message', 'Unknown issue'),
            'suggestions': ["Review the code for potential improvements"],
            'tool': issue.get('tool', 'unknown')
        }

    def _prioritize_feedback(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort feedback by priority (severity, category, line number)"""
        severity_order = {'error': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        
        def sort_key(item):
            severity = item.get('severity', 'info')
            category = item.get('category', 'unknown')
            line = item.get('line', 0)
            return (severity_order.get(severity, 5), category, line)
        
        return sorted(feedback_items, key=sort_key)
