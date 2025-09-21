import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.analyzer import Analyzer

class TestAnalyzer:
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = Analyzer()
        
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        assert hasattr(self.analyzer, 'analysis_tools')
        assert 'flake8' in self.analyzer.analysis_tools
        assert 'radon' in self.analyzer.analysis_tools
        assert 'bandit' in self.analyzer.analysis_tools
        assert 'safety' in self.analyzer.analysis_tools
        assert 'custom' in self.analyzer.analysis_tools

    def test_analyze_empty_diffs(self):
        """Test analysis with empty diffs"""
        diffs = []
        issues = self.analyzer.analyze(diffs)
        assert issues == []

    def test_analyze_with_mock_diffs(self):
        """Test analysis with mock diff data"""
        diffs = [
            {
                "file": "test.py",
                "changes": "+def test_function():\n+    pass\n"
            }
        ]
        
        with patch.object(self.analyzer, '_run_flake8') as mock_flake8, \
             patch.object(self.analyzer, '_run_radon') as mock_radon, \
             patch.object(self.analyzer, '_run_bandit') as mock_bandit, \
             patch.object(self.analyzer, '_run_safety') as mock_safety, \
             patch.object(self.analyzer, '_custom_analysis') as mock_custom:
            
            mock_flake8.return_value = []
            mock_radon.return_value = []
            mock_bandit.return_value = []
            mock_safety.return_value = []
            mock_custom.return_value = []
            
            issues = self.analyzer.analyze(diffs)
            assert isinstance(issues, list)

    def test_run_flake8_success(self):
        """Test flake8 analysis success"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "test.py:1:1: E501 line too long"
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_flake8("test.py", "test content")
            
            assert len(issues) == 1
            assert issues[0]['file'] == "test.py"
            assert issues[0]['line'] == 1
            assert issues[0]['code'] == "E501"
            assert issues[0]['severity'] == 'error'

    def test_run_flake8_timeout(self):
        """Test flake8 analysis timeout"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = TimeoutError("Timeout")
            
            issues = self.analyzer._run_flake8("test.py", "test content")
            assert issues == []

    def test_run_radon_success(self):
        """Test radon complexity analysis success"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "test.py:1:test_function - 15 (F)"
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_radon("test.py", "test content")
            
            assert len(issues) == 1
            assert issues[0]['complexity'] == 15
            assert issues[0]['severity'] == 'high'

    def test_run_bandit_success(self):
        """Test bandit security analysis success"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = '{"results": [{"filename": "test.py", "line_number": 1, "issue_severity": "HIGH", "issue_text": "Test issue", "issue_confidence": "HIGH", "test_id": "B101"}]}'
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_bandit("test.py", "test content")
            
            assert len(issues) == 1
            assert issues[0]['severity'] == 'high'
            assert issues[0]['category'] == 'security'

    def test_custom_analysis_todo_detection(self):
        """Test custom analysis for TODO detection"""
        changes = "+def test():\n+    # TODO: implement this\n+    pass"
        issues = self.analyzer._custom_analysis("test.py", changes)
        
        assert len(issues) == 1
        assert issues[0]['category'] == 'maintenance'
        assert 'TODO' in issues[0]['message']

    def test_custom_analysis_secret_detection(self):
        """Test custom analysis for secret detection"""
        changes = "+password = 'secret123'\n+api_key = 'key123'"
        issues = self.analyzer._custom_analysis("test.py", changes)
        
        assert len(issues) >= 1
        security_issues = [i for i in issues if i['category'] == 'security']
        assert len(security_issues) >= 1

    def test_custom_analysis_large_function(self):
        """Test custom analysis for large function detection"""
        # Create a temporary file with a large function
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def large_function():\n")
            for i in range(60):  # More than 50 lines
                f.write(f"    line_{i} = {i}\n")
            f.write("    return True\n")
            temp_file = f.name
        
        try:
            changes = f"+{open(temp_file).read()}"
            issues = self.analyzer._custom_analysis(temp_file, changes)
            
            large_function_issues = [i for i in issues if 'Large function' in i['message']]
            assert len(large_function_issues) >= 1
        finally:
            os.unlink(temp_file)

    def test_get_severity_from_code(self):
        """Test severity mapping from flake8 codes"""
        assert self.analyzer._get_severity_from_code('E501') == 'error'
        assert self.analyzer._get_severity_from_code('W293') == 'warning'
        assert self.analyzer._get_severity_from_code('F841') == 'error'
        assert self.analyzer._get_severity_from_code('C901') == 'info'

    def test_deduplicate_issues(self):
        """Test issue deduplication"""
        issues = [
            {'file': 'test.py', 'line': 1, 'message': 'Test issue'},
            {'file': 'test.py', 'line': 1, 'message': 'Test issue'},  # Duplicate
            {'file': 'test.py', 'line': 2, 'message': 'Different issue'},
        ]
        
        unique_issues = self.analyzer._deduplicate_issues(issues)
        assert len(unique_issues) == 2

    def test_analyze_with_file_not_found(self):
        """Test analysis when file doesn't exist"""
        diffs = [
            {
                "file": "nonexistent.py",
                "changes": "+def test():\n+    pass\n"
            }
        ]
        
        with patch.object(self.analyzer, '_run_flake8') as mock_flake8:
            mock_flake8.side_effect = FileNotFoundError("File not found")
            
            issues = self.analyzer.analyze(diffs)
            
            # Should have one error issue
            error_issues = [i for i in issues if i['category'] == 'analysis_error']
            assert len(error_issues) == 1

    def test_analyze_with_exception(self):
        """Test analysis when tool raises exception"""
        diffs = [
            {
                "file": "test.py",
                "changes": "+def test():\n+    pass\n"
            }
        ]
        
        with patch.object(self.analyzer, '_run_flake8') as mock_flake8:
            mock_flake8.side_effect = Exception("Unexpected error")
            
            issues = self.analyzer.analyze(diffs)
            
            # Should have one error issue
            error_issues = [i for i in issues if i['category'] == 'analysis_error']
            assert len(error_issues) == 1

    def test_run_safety_success(self):
        """Test safety dependency vulnerability scanning"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = '[{"package": "requests", "installed_version": "2.25.0", "vulnerability": "CVE-2021-1234"}]'
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_safety("test.py", "test content")
            
            assert len(issues) == 1
            assert issues[0]['severity'] == 'high'
            assert issues[0]['category'] == 'security'
            assert 'requests' in issues[0]['message']

    def test_run_safety_no_vulnerabilities(self):
        """Test safety when no vulnerabilities found"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = '[]'
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_safety("test.py", "test content")
            assert issues == []

    def test_run_safety_invalid_json(self):
        """Test safety with invalid JSON response"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = 'invalid json'
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_safety("test.py", "test content")
            assert issues == []

    def test_run_bandit_invalid_json(self):
        """Test bandit with invalid JSON response"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = 'invalid json'
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_bandit("test.py", "test content")
            assert issues == []

    def test_run_radon_no_output(self):
        """Test radon with no output"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = ''
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_radon("test.py", "test content")
            assert issues == []

    def test_run_radon_invalid_output(self):
        """Test radon with invalid output format"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = 'invalid format'
            mock_run.return_value.returncode = 0
            
            issues = self.analyzer._run_radon("test.py", "test content")
            assert issues == []

    def test_custom_analysis_ast_error(self):
        """Test custom analysis with AST parsing error"""
        changes = "+def test():\n+    invalid syntax here"
        
        with patch('ast.parse') as mock_parse:
            mock_parse.side_effect = SyntaxError("Invalid syntax")
            
            issues = self.analyzer._custom_analysis("test.py", changes)
            # Should not crash, just return other issues
            assert isinstance(issues, list)
