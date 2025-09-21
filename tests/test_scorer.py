import pytest
from core.scorer import PRScorer

class TestPRScorer:
    def setup_method(self):
        """Setup test fixtures"""
        self.scorer = PRScorer()
        
    def test_scorer_initialization(self):
        """Test scorer initialization"""
        assert hasattr(self.scorer, 'category_weights')
        assert hasattr(self.scorer, 'severity_penalties')
        assert hasattr(self.scorer, 'tool_weights')
        
        # Check default weights
        assert self.scorer.category_weights['security'] == 0.3
        assert self.scorer.category_weights['error'] == 0.25
        assert self.scorer.category_weights['complexity'] == 0.2
        
        # Check severity penalties
        assert self.scorer.severity_penalties['error'] == 20
        assert self.scorer.severity_penalties['high'] == 15
        assert self.scorer.severity_penalties['medium'] == 10
        
        # Check tool weights
        assert self.scorer.tool_weights['bandit'] == 1.5
        assert self.scorer.tool_weights['safety'] == 1.5
        assert self.scorer.tool_weights['flake8'] == 1.0

    def test_score_empty_issues(self):
        """Test scoring with no issues"""
        issues = []
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] == 100
        assert score_data['grade'] == 'A+'
        assert score_data['summary'] == 'No issues found - excellent code quality!'
        assert 'security' in score_data['breakdown']
        assert 'quality' in score_data['breakdown']
        assert 'maintainability' in score_data['breakdown']
        assert 'style' in score_data['breakdown']

    def test_score_single_issue(self):
        """Test scoring with a single issue"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'medium',
                'category': 'style',
                'tool': 'flake8',
                'message': 'Line too long'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert score_data['total_score'] > 0
        assert 'grade' in score_data
        assert 'breakdown' in score_data
        assert 'summary' in score_data
        assert 'metrics' in score_data
        assert 'recommendations' in score_data

    def test_score_multiple_issues(self):
        """Test scoring with multiple issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit',
                'message': 'Security issue'
            },
            {
                'file': 'test.py',
                'line': 2,
                'severity': 'medium',
                'category': 'style',
                'tool': 'flake8',
                'message': 'Style issue'
            },
            {
                'file': 'test.py',
                'line': 3,
                'severity': 'low',
                'category': 'maintenance',
                'tool': 'custom',
                'message': 'Maintenance issue'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert score_data['total_score'] > 0
        assert len(score_data['recommendations']) > 0
        
        # Check that security issues are prioritized
        security_recs = [r for r in score_data['recommendations'] if 'security' in r.lower()]
        assert len(security_recs) > 0

    def test_score_high_severity_issues(self):
        """Test scoring with high severity issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'error',
                'category': 'error',
                'tool': 'flake8',
                'message': 'Syntax error'
            },
            {
                'file': 'test.py',
                'line': 2,
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit',
                'message': 'Critical security issue'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 50  # Should be significantly penalized
        assert score_data['grade'] in ['D', 'F']
        assert 'error' in score_data['summary'].lower() or 'high' in score_data['summary'].lower()

    def test_score_security_issues(self):
        """Test scoring with security issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit',
                'message': 'Security vulnerability'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert 'security' in score_data['summary'].lower()
        
        # Check for security recommendations
        security_recs = [r for r in score_data['recommendations'] if 'security' in r.lower()]
        assert len(security_recs) > 0

    def test_score_complexity_issues(self):
        """Test scoring with complexity issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'medium',
                'category': 'complexity',
                'tool': 'radon',
                'message': 'High complexity function',
                'complexity': 15
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert 'complexity' in score_data['summary'].lower()
        
        # Check for complexity recommendations
        complexity_recs = [r for r in score_data['recommendations'] if 'complex' in r.lower()]
        assert len(complexity_recs) > 0

    def test_score_style_issues(self):
        """Test scoring with style issues"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'low',
                'category': 'style',
                'tool': 'flake8',
                'message': 'Style issue'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert score_data['total_score'] > 80  # Style issues should have less impact
        
        # Check for style recommendations
        style_recs = [r for r in score_data['recommendations'] if 'style' in r.lower()]
        assert len(style_recs) > 0

    def test_calculate_grade(self):
        """Test grade calculation"""
        # Test different score ranges
        assert self.scorer._calculate_grade(100) == 'A+'
        assert self.scorer._calculate_grade(95) == 'A+'
        assert self.scorer._calculate_grade(90) == 'A'
        assert self.scorer._calculate_grade(85) == 'A-'
        assert self.scorer._calculate_grade(80) == 'B+'
        assert self.scorer._calculate_grade(75) == 'B'
        assert self.scorer._calculate_grade(70) == 'B-'
        assert self.scorer._calculate_grade(65) == 'C+'
        assert self.scorer._calculate_grade(60) == 'C'
        assert self.scorer._calculate_grade(55) == 'C-'
        assert self.scorer._calculate_grade(50) == 'D'
        assert self.scorer._calculate_grade(30) == 'F'

    def test_group_issues_by_category(self):
        """Test grouping issues by category"""
        issues = [
            {'category': 'security', 'severity': 'high'},
            {'category': 'style', 'severity': 'low'},
            {'category': 'security', 'severity': 'medium'},
            {'category': 'complexity', 'severity': 'medium'}
        ]
        
        grouped = self.scorer._group_issues_by_category(issues)
        
        assert 'security' in grouped
        assert 'style' in grouped
        assert 'complexity' in grouped
        assert len(grouped['security']) == 2
        assert len(grouped['style']) == 1
        assert len(grouped['complexity']) == 1

    def test_calculate_category_penalty(self):
        """Test category penalty calculation"""
        issues = [
            {'severity': 'high', 'tool': 'bandit'},
            {'severity': 'medium', 'tool': 'flake8'}
        ]
        
        penalty = self.scorer._calculate_category_penalty('security', issues)
        
        assert penalty > 0
        # Security issues should have higher penalty
        assert penalty > self.scorer._calculate_category_penalty('style', issues)

    def test_calculate_metrics(self):
        """Test metrics calculation"""
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit'
            },
            {
                'file': 'test.py',
                'line': 2,
                'severity': 'medium',
                'category': 'style',
                'tool': 'flake8'
            },
            {
                'file': 'other.py',
                'line': 3,
                'severity': 'low',
                'category': 'maintenance',
                'tool': 'custom'
            }
        ]
        
        metrics = self.scorer._calculate_metrics(issues)
        
        assert metrics['total_issues'] == 3
        assert metrics['files_affected'] == 2
        assert metrics['lines_affected'] == 3
        assert metrics['issues_by_severity']['high'] == 1
        assert metrics['issues_by_severity']['medium'] == 1
        assert metrics['issues_by_severity']['low'] == 1
        assert metrics['issues_by_category']['security'] == 1
        assert metrics['issues_by_category']['style'] == 1
        assert metrics['issues_by_category']['maintenance'] == 1
        assert metrics['issues_by_tool']['bandit'] == 1
        assert metrics['issues_by_tool']['flake8'] == 1
        assert metrics['issues_by_tool']['custom'] == 1

    def test_generate_recommendations(self):
        """Test recommendation generation"""
        issues = [
            {
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit'
            },
            {
                'severity': 'error',
                'category': 'error',
                'tool': 'flake8'
            },
            {
                'severity': 'medium',
                'category': 'complexity',
                'tool': 'radon'
            }
        ]
        
        category_scores = {'security': 60, 'error': 40, 'complexity': 70}
        recommendations = self.scorer._generate_recommendations(issues, category_scores)
        
        assert len(recommendations) > 0
        
        # Check for specific recommendation types
        security_recs = [r for r in recommendations if 'security' in r.lower()]
        error_recs = [r for r in recommendations if 'error' in r.lower()]
        complexity_recs = [r for r in recommendations if 'complex' in r.lower()]
        
        assert len(security_recs) > 0
        assert len(error_recs) > 0
        assert len(complexity_recs) > 0

    def test_generate_summary(self):
        """Test summary generation"""
        issues = [
            {'severity': 'error', 'category': 'error'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'medium', 'category': 'style'}
        ]
        
        category_scores = {'error': 40, 'security': 60, 'style': 80}
        summary = self.scorer._generate_summary(issues, 75.0, category_scores)
        
        assert '75.0' in summary
        assert 'error' in summary.lower()
        assert 'high' in summary.lower()
        assert 'security' in summary.lower()

    def test_score_with_many_issues(self):
        """Test scoring with many issues"""
        issues = []
        for i in range(25):  # More than 20 issues
            issues.append({
                'file': f'test{i}.py',
                'line': i,
                'severity': 'medium',
                'category': 'style',
                'tool': 'flake8',
                'message': f'Issue {i}'
            })
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert len(score_data['recommendations']) > 0
        
        # Should recommend breaking PR into smaller changes
        large_pr_recs = [r for r in score_data['recommendations'] if 'smaller' in r.lower()]
        assert len(large_pr_recs) > 0

    def test_score_tool_specific_recommendations(self):
        """Test tool-specific recommendations"""
        issues = [
            {'tool': 'bandit', 'category': 'security'},
            {'tool': 'radon', 'category': 'complexity'}
        ]
        
        category_scores = {'security': 60, 'complexity': 70}
        recommendations = self.scorer._generate_recommendations(issues, category_scores)
        
        # Check for tool-specific recommendations
        bandit_recs = [r for r in recommendations if 'security' in r.lower()]
        radon_recs = [r for r in recommendations if 'complexity' in r.lower()]
        
        assert len(bandit_recs) > 0
        assert len(radon_recs) > 0

    def test_score_edge_cases(self):
        """Test scoring edge cases"""
        # Test with unknown category
        issues = [
            {
                'file': 'test.py',
                'line': 1,
                'severity': 'medium',
                'category': 'unknown',
                'tool': 'unknown',
                'message': 'Unknown issue'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert 'unknown' in score_data['breakdown']
        
        # Test with missing fields
        issues = [
            {
                'file': 'test.py',
                'message': 'Issue with missing fields'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        assert score_data['total_score'] < 100
        assert 'unknown' in score_data['breakdown']

    def test_score_breakdown_calculation(self):
        """Test score breakdown calculation"""
        issues = [
            {
                'severity': 'high',
                'category': 'security',
                'tool': 'bandit'
            },
            {
                'severity': 'medium',
                'category': 'style',
                'tool': 'flake8'
            }
        ]
        
        score_data = self.scorer.score(issues)
        
        # Check that all categories have scores
        assert 'security' in score_data['breakdown']
        assert 'style' in score_data['breakdown']
        
        # Security should have lower score due to higher penalty
        assert score_data['breakdown']['security'] < score_data['breakdown']['style']
