import subprocess
import re
import ast
import os
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class Analyzer:
    def __init__(self):
        self.analysis_tools = {
            'flake8': self._run_flake8,
            'radon': self._run_radon,
            'bandit': self._run_bandit,
            'safety': self._run_safety,
            'custom': self._custom_analysis
        }

    def analyze(self, diffs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Comprehensive analysis of code changes
        Returns structured issues with severity, category, and suggestions
        """
        all_issues = []
        
        for diff in diffs:
            file_path = diff["file"]
            changes = diff["changes"]
            
            logger.info(f"Analyzing file: {file_path}")
            
            # Run all analysis tools
            for tool_name, tool_func in self.analysis_tools.items():
                try:
                    issues = tool_func(file_path, changes)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error running {tool_name} on {file_path}: {e}")
                    all_issues.append({
                        'file': file_path,
                        'tool': tool_name,
                        'severity': 'error',
                        'category': 'analysis_error',
                        'message': f"Analysis failed: {str(e)}",
                        'line': 0
                    })
        
        return self._deduplicate_issues(all_issues)

    def _run_flake8(self, file_path: str, changes: str) -> List[Dict[str, Any]]:
        """Run flake8 style and error checking"""
        issues = []
        
        try:
            result = subprocess.run(
                ["flake8", "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s", file_path],
                capture_output=True, text=True, timeout=30
            )
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            issues.append({
                                'file': parts[0],
                                'line': int(parts[1]),
                                'column': int(parts[2]),
                                'code': parts[3].split()[0],
                                'message': ' '.join(parts[3].split()[1:]),
                                'severity': self._get_severity_from_code(parts[3].split()[0]),
                                'category': 'style',
                                'tool': 'flake8'
                            })
        except subprocess.TimeoutExpired:
            logger.warning(f"flake8 timeout for {file_path}")
        except Exception as e:
            logger.error(f"flake8 error for {file_path}: {e}")
            
        return issues

    def _run_radon(self, file_path: str, changes: str) -> List[Dict[str, Any]]:
        """Run radon complexity analysis"""
        issues = []
        
        try:
            # Cyclomatic complexity
            result = subprocess.run(
                ["radon", "cc", "-a", file_path],
                capture_output=True, text=True, timeout=30
            )
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line and '(' in line:
                        # Parse: file:line:function - complexity (grade)
                        match = re.match(r'(.+):(\d+):(.+)\s+-\s+(\d+)\s+\(([A-F])\)', line)
                        if match:
                            complexity = int(match.group(4))
                            grade = match.group(5)
                            
                            if complexity > 10 or grade in ['D', 'F']:
                                issues.append({
                                    'file': match.group(1),
                                    'line': int(match.group(2)),
                                    'function': match.group(3),
                                    'complexity': complexity,
                                    'grade': grade,
                                    'severity': 'high' if complexity > 15 else 'medium',
                                    'category': 'complexity',
                                    'message': f"High complexity ({complexity}) - consider refactoring",
                                    'tool': 'radon'
                                })
        except Exception as e:
            logger.error(f"radon error for {file_path}: {e}")
            
        return issues

    def _run_bandit(self, file_path: str, changes: str) -> List[Dict[str, Any]]:
        """Run bandit security analysis"""
        issues = []
        
        try:
            result = subprocess.run(
                ["bandit", "-f", "json", file_path],
                capture_output=True, text=True, timeout=30
            )
            
            if result.stdout:
                import json
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    issues.append({
                        'file': issue['filename'],
                        'line': issue['line_number'],
                        'severity': issue['issue_severity'].lower(),
                        'category': 'security',
                        'message': issue['issue_text'],
                        'confidence': issue['issue_confidence'],
                        'tool': 'bandit',
                        'test_id': issue['test_id']
                    })
        except Exception as e:
            logger.error(f"bandit error for {file_path}: {e}")
            
        return issues

    def _run_safety(self, file_path: str, changes: str) -> List[Dict[str, Any]]:
        """Run safety for dependency vulnerabilities"""
        issues = []
        
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.stdout:
                import json
                data = json.loads(result.stdout)
                for vuln in data:
                    issues.append({
                        'file': 'requirements.txt',
                        'severity': 'high',
                        'category': 'security',
                        'message': f"Vulnerable dependency: {vuln['package']} {vuln['installed_version']}",
                        'vulnerability': vuln['vulnerability'],
                        'tool': 'safety'
                    })
        except Exception as e:
            logger.error(f"safety error: {e}")
            
        return issues

    def _custom_analysis(self, file_path: str, changes: str) -> List[Dict[str, Any]]:
        """Custom analysis for common issues"""
        issues = []
        
        # Check for TODO/FIXME comments
        todo_pattern = r'(TODO|FIXME|HACK|XXX):\s*(.+)'
        for i, line in enumerate(changes.split('\n'), 1):
            if line.startswith('+'):
                match = re.search(todo_pattern, line, re.IGNORECASE)
                if match:
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'severity': 'low',
                        'category': 'maintenance',
                        'message': f"Found {match.group(1)}: {match.group(2)}",
                        'tool': 'custom'
                    })
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            for i, line in enumerate(changes.split('\n'), 1):
                if line.startswith('+') and re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'severity': 'high',
                        'category': 'security',
                        'message': "Potential hardcoded secret detected",
                        'tool': 'custom'
                    })
        
        # Check for large functions
        if file_path.endswith('.py'):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                            if lines > 50:
                                issues.append({
                                    'file': file_path,
                                    'line': node.lineno,
                                    'severity': 'medium',
                                    'category': 'maintainability',
                                    'message': f"Large function ({lines} lines) - consider breaking down",
                                    'tool': 'custom'
                                })
            except Exception as e:
                logger.error(f"AST analysis error for {file_path}: {e}")
        
        return issues

    def _get_severity_from_code(self, code: str) -> str:
        """Map flake8 error codes to severity levels"""
        if code.startswith('E'):
            return 'error'
        elif code.startswith('W'):
            return 'warning'
        elif code.startswith('F'):
            return 'error'
        else:
            return 'info'

    def _deduplicate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate issues based on file, line, and message"""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            key = (issue.get('file', ''), issue.get('line', 0), issue.get('message', ''))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues
